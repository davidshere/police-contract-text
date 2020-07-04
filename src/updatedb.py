import utils


if __name__ == "__main__":
    jd_to_soup_map = utils.get_jurisdiction_and_link_soup()
    jd_to_doc_map = utils.get_jurisdictions_and_pdf_links(jd_to_soup_map)

    state_jd_pdf_map = utils.transform_from_jd_to_state(jd_to_doc_map)

    existing_files_map = utils.load_contract_paths()
    missing_files = utils.find_missing_docs(state_jd_pdf_map, existing_files_map)

    print(f"Found {len(missing_files)} missing files")

