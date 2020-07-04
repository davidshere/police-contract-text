import json
import urllib.parse

from src import utils

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


if __name__ == "__main__":
    jd_to_soup_map = utils.get_jurisdiction_and_link_soup()
    jd_to_doc_map = utils.get_jurisdictions_and_pdf_links(jd_to_soup_map)

    state_jd_pdf_map = utils.transform_from_jd_to_state(jd_to_doc_map)

    existing_files_map = utils.load_contract_paths()

    directory = merge_dicts(state_jd_pdf_map, existing_files_map)
    with open('directory.json', 'w') as f:
        json.dump(directory, f, indent=4)
