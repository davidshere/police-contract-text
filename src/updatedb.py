import collections
import glob
import json
import pathlib
import os
import urllib.parse
from typing import Dict

import utils
import generate_directory

MAX_FILE_SIZE = 1024 * 350


def split_large_files(directory: Dict, max_size: int = MAX_FILE_SIZE):
    """
    Github only indexes files up to a 380 something KB, so we're splitting
    files above a certain length so that they all get indexed.
    """
    new_dir = directory.copy()
    contract_paths = [pathlib.Path(p) for p in glob.glob('./contracts/*/*/*')]

    for path in contract_paths:
        _, state, jd, filename = str(path).split('/')
        old_file_title = filename[:-4]

        with path.open() as f:
            full_text = f.read()

        # Using the number of characters as opposed to some other measure of size
        # because it should make it easier to be consistent
        if len(full_text) > max_size:
            num_groups = 1 + len(full_text) // max_size
            for i in range(num_groups):
                new_path = str(path).replace('.txt', f' {i + 1}.txt')

                # chunking
                starting_index = i * max_size
                ending_index = (i + 1) * max_size
                text_chunk = full_text[starting_index:ending_index]

                # Write the new file
                with open(new_path, 'w') as f:
                    f.write(text_chunk)

                # Write the directory entries
                new_filename = new_path.split('/')[-1]

                # turn ./contracts/Illinois/Chicago/contract.txt into contract
                new_file_title = new_filename[:-4]

                # Add a new record to the directory, with the correct text url
                new_document_record = new_dir[state][jd][old_file_title].copy()
                quoted_path_in_repo = urllib.parse.quote('/'.join(str(new_path).split('/')[1:]))
                new_document_record['textUrl'] = generate_directory.FMT_URL.format(quoted_path_in_repo)
                new_dir[state][jd][new_file_title] = new_document_record

            # Remove the old file
            # path.unlink()

            # Remove the old file from the directory
            del directory[state][jd][old_file_title]

    return new_dir

if __name__ == "__main__":
    ctp_soup = utils.fetch_check_the_police_soup()

    jd_to_soup_map = utils.get_jurisdiction_and_link_soup(ctp_soup)

    # We've got a few methods of pulling contract from checkthepolice.org
    # 1. Look for jurisdictions with a check mark
    jd_to_doc_map = utils.get_jurisdictions_and_pdf_links(jd_to_soup_map)
    # 2. Add jurisdictions that we know exist but that weren't caught above for some reason
    jd_to_doc_map.update(utils.hard_coded_jurisdictions_and_links)
    # 3. Add the smaller cities
    # jd_to_doc_map.update(utils.get_smaller_cities_and_bor_mapping(ctp_soup))


    state_jd_pdf_map = utils.transform_from_jd_to_state(jd_to_doc_map)
    existing_files_map = utils.load_contract_paths()
    missing_files = utils.find_missing_docs(state_jd_pdf_map, existing_files_map)

    failed_to_parse = []
    print(f"Found {len(missing_files)} missing files")
    for missing_file in missing_files:
        state, jurisdiction, source, filename = missing_file
        print(f"Fetching/parsing {state} {jurisdiction} {filename}")
        result = utils.get_pdf_from_link(source['pdfUrl'])
        if result is None:
            failed_to_parse.append(missing_file)
            continue

        if jurisdiction != 'State':
            outpath = pathlib.Path('./contracts') / state / jurisdiction / f"{filename}.txt"
        else:
            outpath = pathlib.Path('./contracts') / state / 'State' / f"{filename}.txt"

        if not outpath.parent.is_dir():
            os.makedirs(outpath.parent, exist_ok=True)
        with outpath.open('w') as f:
            f.write(result)

    # Regenerate the directory
    directory = generate_directory.generate()

    # Add filenames
    for state, jurisdictions in directory.items():
        for jurisdiction, documents in jurisdictions.items():
            for document, data in documents.items():
                data['title'] = f"{document}"

    # make the pdfMap
    pdf_map = utils.recursive_dd()
    for state, jurisdictions in directory.items():
        for jurisdiction, documents in jurisdictions.items():
            for document, data in documents.items():
                pdf_map[f"{state}/{jurisdiction}/{document}.txt"] = data['pdfUrl']

    # make the tag map
    tag_map = collections.defaultdict(list)
    for state, jurisdictions in directory.items():
        for jurisdiction, documents in jurisdictions.items():
            for document, data in documents.items():
                for tag in data['tags']:
                    tag_map[tag].append({'pdfUrl': data['pdfUrl'], 'textUrl': data['textUrl']})


    with open('directory.json', 'w') as f:
        json.dump(directory, f, indent=4)

    with open('pdf_map.json', 'w') as f:
        json.dump(pdf_map, f, indent=4)

    with open('tag_map.json', 'w') as f:
        json.dump(tag_map, f, indent=4)


