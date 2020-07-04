import collections
import pathlib
import re
from typing import Dict

import requests
import textract
from bs4 import BeautifulSoup
from bs4.element import Tag

BASE_URL = "https://www.checkthepolice.org"

CITY_REGEX_PATTERN = re.compile(
    r'(.*) (Metropolitan Police Department|Police Bureau|Sheriff\'s Office|Division of Police|Bureau of Police|Police Department).*')

"""
Some basic utils
"""



def recursive_dd():
    """
    No one function should have all that power!
    
    Taken from: https://stackoverflow.com/questions/19189274/nested-defaultdict-of-defaultdict 
    """
    return collections.defaultdict(recursive_dd)

"""
Map states to the jurisdictions we have and jurisdictions back to their
states
"""

STATE_CITY_MAP = {
    "New Mexico": ['Albuquerque'],
    "California": ['Anaheim', 'Bakersfield', 'Chula Vista', 'Fremont', 'Fresno', 'Glendale', 'Irvine', 'Long Beach',
                   'Los Angeles', 'Oakland', 'Riverside', 'Sacramento', 'San Diego', 'San Francisco', 'San Jose',
                   'Santa Ana', 'Stockton'],
    "Alaska": ['Anchorage'],
    "Colorado": ['Aurora', "Denver"],
    "Texas": ['Austin', 'Corpus Christi', 'Dallas', 'El Paso', 'Fort Worth', 'Houston', 'Laredo', 'San Antonio'],
    "Maryland": ['Baltimore'],
    "Louisiana": ['Baton Rouge'],
    "Massachusetts": ['Boston'],
    "New York": ['Buffalo', 'New York', 'Rochester'],
    "Arizona": ['Chandler', 'Phoenix', "Tucson"],
    "Illinois": ['Chicago'],
    "Michigan": ['Detroit'],
    "Indiana": ["Fort Wayne", "Indianapolis"],
    "Ohio": ['Cincinnati', 'Cleveland', 'Columbus'],
    "Nevada": ['Henderson', 'Las Vegas Metropolitan', 'North Las Vegas', 'Reno'],
    "Florida": ['Hialeah', 'Jacksonville', 'Miami', 'Orlando', 'St. Petersburg', 'Tampa'],
    "New Jersey": ['Jersey City', 'Newark'],
    "Nebraska": ['Lincoln', 'Omaha'],
    "Kentucky": ['Louisville'],
    "Wisconsin": ['Madison', 'Milwaukee'],
    "Tennessee": ['Memphis', 'Metropolitan Nashville'],
    "Minnesota": ["Minneapolis", "St. Paul"],
    "Oklahoma": ['Oklahoma City', "Tulsa"],
    "Pennsylvania": ['Philadelphia', 'Pittsburgh'],
    "Oregon": ['Portland'],
    "Washington": ['Seattle', 'Spokane'],
    "Missouri": ['St. Louis Metropolitan'],
    "Washington, DC": ["Washington DC Metropolitan"],
    "Kansas": ['Wichita'],
}

CITY_TO_STATE_MAP = dict()
for state in STATE_CITY_MAP:
    for city in STATE_CITY_MAP[state]:
        CITY_TO_STATE_MAP[city] = state

"""
Utils for fetching and parsing data from checkthepolice.org
"""


def get_jurisdiction_and_link_soup() -> Dict[str, Tag]:
    """
    Hits checkthepolice.org and returns a list of
    BeautifulSoup objects containing
    :return:
    """
    db_page = f"{BASE_URL}/database"

    base_page_html = requests.get(db_page).text
    base_page_soup = BeautifulSoup(base_page_html, 'lxml')
    contract_soups = list(base_page_soup.find_all('div', {'class': 'sqs-block-content'}))[0]
    jurisdiction_to_soup_map = {}
    for jd in contract_soups:
        if jd.strong and '✔️' in jd.strong.text:
            try:
                jurisdiction_name = CITY_REGEX_PATTERN.findall(jd.strong.text)[0]
                jurisdiction_to_soup_map[jurisdiction_name[0]] = jd
            except IndexError:
                print('failed', jd.strong.text)
    return jurisdiction_to_soup_map


def parse_one_jurisdiction(jd: BeautifulSoup) -> Dict[str, str]:
    """
    This function breaks down the soup object containing links
    for a particular jurisdiction
    """
    link_map = dict()
    for asset_link in jd.find_all('a'):
        category = asset_link.text
        href = asset_link.get('href')
        if href and href.startswith('/s'):
            url = f'{BASE_URL}{href}'
        elif href and 'muckrock' in href:
            continue
        else:
            url = href

        link_map[category] = url
    return link_map


def get_jurisdictions_and_pdf_links(jurisdictions: Dict[str, Tag]) -> Dict[str, Dict[str, str]]:
    all_jurisdiction_links = dict()
    for jd, soup_data in jurisdictions.items():
        all_jurisdiction_links[jd] = parse_one_jurisdiction(soup_data)
    return all_jurisdiction_links


"""
Utils for reading the existing contract directory and diffing it
with what we fetch from checkthepolice.org
"""
def load_contract_paths():
    existing_paths = recursive_dd()

    base_path = pathlib.Path('./contracts')
    for state_dir in base_path.iterdir():
        state_name = state_dir.name
        for f in state_dir.iterdir():

            # In this case it's a BOR
            if not f.is_dir():
                existing_paths[state_name][f"{state_name} Police Bill of Rights"] = str(f)
            else:
                for path in f.iterdir():
                    jurisdiction = path.parent.name
                    existing_paths[state_name][jurisdiction][path.name] = str(path)
    return existing_paths


def find_missing_docs(map_from_web, map_from_disk):
    # TODO: This probably can't just be a list...
    missing_files = []

    # maps the expected file path to the URL
    other_missing_files = {}
    for state, jds in map_from_web.items():
        for jd, files in jds.items():

            # If the whole jurisdiction is missing
            if jd not in map_from_disk[state]:
                for file in files:
                    missing_files.append((state, jd, files[file], file))

            else:
                # Make sure every file is there
                for file in files:
                    if 'Bill' in jd:
                        expected_path = pathlib.Path('./contracts') / state / f"{jd}.txt"
                    else:
                        expected_path = pathlib.Path("./contracts") / state / jd / f"{file}.txt"

                    if not expected_path.exists():
                        missing_files.append(
                            (
                                state,
                                jd,
                                files[file] if 'Bill' not in jd else {'pdfUrl': files[file]},
                                file if 'Bill' not in jd else jd
                            )
                        )
    return missing_files

"""
Utils for fetching and parsing PDF files
"""
def get_pdf_from_link(url):
    if url.endswith('dl=0'):
        url = url[:-1] + "1"

    response = requests.get(url)
    with open('/tmp/contract.pdf', 'wb') as f:
        f.write(response.content)

    try:
        text_as_bytes = textract.process(f.name, method='tesseract', language='eng')
        return text_as_bytes.decode()
    except textract.exceptions.ShellError:
        print(f"Failed to parse {url}")
        return None


"""
Utils for transforming between jurisdiction level to the state level
"""


def transform_from_jd_to_state(
        jurisdiction_map: Dict[str, Dict[str, str]]
) -> Dict[str, Dict[str, str]]:
    """
    Transform the jurisdiction-based mapping to a state-based
    mapping.
    :param jurisdiction_map:
    :return:
    """
    directory = recursive_dd()
    for jurisdiction, docs in jurisdiction_map.items():
        state = CITY_TO_STATE_MAP[jurisdiction]
        for link in docs:
            if 'bill' in link.lower():
                directory[state]['State'][link]['pdfUrl'] = docs[link]
            else:
                directory[state][jurisdiction][link]['pdfUrl'] = docs[link]
    return directory



if __name__ == "__main__":
    jd_to_soup_map = get_jurisdiction_and_link_soup()
    chicago_soup = jd_to_soup_map['Chicago']
    print(parse_one_jurisdiction(chicago_soup))
