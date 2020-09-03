import os
from collections import defaultdict
from pathlib import PurePath, Path


class FileSystem:
    def __init__(self, base_path):
        self.base_path = base_path

    def exists(self, path):
        return Path(path).exists()

    def read_file(self, path):
        if not self.exists(path):
            return ''
        with open(path) as file:
            return file.read()

    def read_filetree(self):
        return [
            Node(PurePath(path), filenames)
            for path, _, filenames
            in os.walk(self.base_path)
        ]


class Node:
    def __init__(self, path, filenames):
        self.path = path
        self.filenames = set(filenames)
        self.extensions = ExtensionMap(filenames)

    def files(self, extension=''):
        return self.extensions.get(extension, self.filenames)

    def __repr__(self):
        return f'Node({self.path})'


class ExtensionMap:
    def __init__(self, files):
        self._map = defaultdict(list)
        self._files = files
        for file_name in files:
            if '.' not in file_name:
                continue
            key = file_name.split('.')[1]
            self._map[key].append(file_name)

    def get(self, extension, default=[]):
        return self._map.get(extension, default)
