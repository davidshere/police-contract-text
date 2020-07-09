import json

from pathlib import Path
from typing import Dict, Union


class Directory:
    """

    """
    def __init__(self, directory: Dict):
        self._dir = directory

    def apply(self):
        """
        Apply a function to each item in a directory
        :return:
        """
        pass

    @classmethod
    def load_json(cls, path_to_directory: Union[str, Path]):
        with open(path_to_directory, 'r') as f:
            return Directory(json.load(f))
