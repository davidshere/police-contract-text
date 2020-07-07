import json
import urllib.parse

import pandas as pd

import utils

FMT_URL = "https://raw.githubusercontent.com/PoliceContracts/PoliceContracts/master/{}"

def merge_dicts(pdf_map, file_map):
    merged = utils.recursive_dd()

    for state, jds in file_map.items():
        for jd, files in jds.items():
            for filename, path in files.items():
                if filename.endswith('.txt'):
                    doc_name = filename[:-4]
                else:
                    doc_name = filename

                # generate proper URLs for the text documents
                quoted_path_in_repo = urllib.parse.quote('/'.join(path.split('/')[1:]))
                text_url = FMT_URL.format(quoted_path_in_repo)
                merged[state][jd][doc_name].update({'textUrl': text_url})

                # add the URLs for the PDFs
                pdfUrl = pdf_map[state][jd][doc_name]['pdfUrl']
                merged[state][jd][doc_name].update({'pdfUrl': pdfUrl})
    return merged


def add_tags_to_directory(tags, directory):
    for tag in tags:
        document_name = tag['associated filename'][:-4]

        if 'Bill' in tag['city/state']:
            jurisdiction = 'State'
            state = ''.join(tag['city/state'].split(' ')[:-4])
        else:
            jurisdiction = tag['city/state']
            state = utils.CITY_TO_STATE_MAP[tag['city/state']]

        entry = directory[state][jurisdiction][document_name]

        if 'tags' not in entry:
            entry['tags'] = set()
        entry['tags'].add(tag['category'])

    for state in directory:
        for jd, files in directory[state].items():
            for file in files:
                if 'tags' in files[file]:
                    files[file]['tags'] = list(files[file]['tags'])

    return directory

def generate():
    soup = utils.fetch_check_the_police_soup()
    jd_to_soup_map = utils.get_jurisdiction_and_link_soup(soup)
    jd_to_doc_map = utils.get_jurisdictions_and_pdf_links(jd_to_soup_map)
    jd_to_doc_map.update(utils.hard_coded_jurisdictions_and_links)

    state_jd_pdf_map = utils.transform_from_jd_to_state(jd_to_doc_map)

    existing_files_map = utils.load_contract_paths()
    directory = merge_dicts(state_jd_pdf_map, existing_files_map)

    df = pd.read_csv('new_tags.csv', encoding='latin')
    df['associated filename'].fillna('', inplace=True)
    tags = df.to_dict(orient='records')

    directory = add_tags_to_directory(tags, directory)

    # we've got some phantom records in here, data that
    # is missing for one reason or another. I know this is
    # a mess. I'm sorry.
    to_delete = []
    for state, jurisdictions in directory.items():
        for jurisdiction, documents in jurisdictions.items():
            for document in documents:
                if document == "":
                    to_delete.append((state, jurisdiction, document))

    for state, jd, doc in to_delete:
        del directory[state][jd]

    state_to_delete = []
    for state, jurisdictions in directory.items():
        # Ack!!
        if jurisdictions == dict() or state == 'NewMexico':
            state_to_delete.append(state)
    for state in state_to_delete:
        del directory[state]



    return directory

if __name__ == "__main__":
    directory = generate()
    with open('directory.json', 'w') as f:
        json.dump(directory, f, indent=4)
