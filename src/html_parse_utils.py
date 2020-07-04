import re
from typing import Dict

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

BASE_URL = "https://www.checkthepolice.org"

CITY_REGEX_PATTERN = re.compile(r'(.*) (Metropolitan Police Department|Police Bureau|Sheriff\'s Office|Division of Police|Bureau of Police|Police Department).*')


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


def get_jurisdictions_and_pdf_links(jursdictions) -> Dict[str, Dict[str, str]]:
    all_jurisdiction_links = dict()
    for jurisdiction, soup_data in jursdictions.items():
        all_jurisdiction_links[jurisdiction] = parse_one_jurisdiction(soup_data)
    return all_jurisdiction_links


if __name__ == "__main__":
    jd_to_soup_map = get_jurisdiction_and_link_soup()
    chicago_soup = jd_to_soup_map['Chicago']
    print(parse_one_jurisdiction(chicago_soup))
