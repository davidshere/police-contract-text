import pathlib
import os

import utils


if __name__ == "__main__":
    jd_to_soup_map = utils.get_jurisdiction_and_link_soup()
    jd_to_doc_map = utils.get_jurisdictions_and_pdf_links(jd_to_soup_map)

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


