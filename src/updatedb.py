import pathlib
import os

import utils

# The HTML isn't we're pulling from isn't entirely consistent, so we've got a "good enough"
# scraper and this hard coded map for things that we don't catch
hard_coded_jurisdictions_and_links = {
    'Honolulu': {
        'Police Union Contract': 'https://www.checkthepolice.org/s/Honolulu-Police-Contract.pdf',
    },
    'Kansas City, MO': {
        'Police Union Contract': 'https://www.checkthepolice.org/s/Kansas-City-MO-Police-Contract.pdf'
    },
    'Lexington': {
        'Police Union Contract': 'https://www.checkthepolice.org/s/Lexington-Police-Contract.pdf'
    },
    'Mesa': {
        'Police Union Contract': 'https://www.checkthepolice.org/s/Mesa-Police-Union-Contract.pdf'
    },
    'Toledo': {
        'Police Union Contract': 'https://www.checkthepolice.org/s/Toledo-Police-Contract.pdf'
    },
}

if __name__ == "__main__":
    ctp_soup = utils.fetch_check_the_police_soup()

    jd_to_soup_map = utils.get_jurisdiction_and_link_soup(ctp_soup)

    # We've got a few methods of pulling contract from checkthepolice.org
    # 1. Look for jurisdictions with a check mark
    jd_to_doc_map = utils.get_jurisdictions_and_pdf_links(jd_to_soup_map)
    # 2. Add jurisdictions that we know exist but that weren't caught above for some reason
    jd_to_doc_map.update(hard_coded_jurisdictions_and_links)
    # 3. Add the smaller cities
    jd_to_doc_map.update(utils.get_smaller_cities_mapping(ctp_soup))


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


