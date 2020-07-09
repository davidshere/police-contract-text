from pathlib import Path

from src.directory import Directory

RESOURCE_PATH = Path("/home/david/src/police-contract-text/resources/")
TEST_DIRECTORY_PATH = RESOURCE_PATH / 'test_directory.json'

TEST_DIRECTORY = {
    "Illinois": {
        "State": {
            "Illinois Police Bill of Rights": {
                "textUrl": "location.txt",
                "pdfUrl": "file.pdf",
                "tags": [
                    "does bad things",
                    "is a real meanie"
                ],
                "title": "police union contract"
            }
        }
    }
}

def test_directory():
    directory = Directory.load_json(TEST_DIRECTORY_PATH)
    assert directory._dir == TEST_DIRECTORY
