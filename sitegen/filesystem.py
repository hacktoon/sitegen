import os
from collections import defaultdict
from pathlib import PurePath


class FileSystem:
    def read(self, data_path):
        return [FileSystemNode(*params) for params in os.walk(data_path)]


class FileSystemNode:
    def __init__(self, path, folders, files):
        self.path = PurePath(path)
        self.folder_names = set(folders)
        self.file_names = set(files)
        self.extension_map = ExtensionMap(files)

    def read(self, filename, default=''):
        if not self.exists(filename):
            return default
        file_path = self.path / filename
        with open(file_path) as fp:
            return fp.read()

    def files(self, extension=''):
        file_names = self.extension_map.get(extension, self.file_names)
        return [self.path / file for file in file_names]

    def folders(self):
        return [self.path / folder for folder in self.folder_names]

    def exists(self, name):
        return name in self.folder_names or name in self.file_names

    def __repr__(self):
        return f'FileSystemNode({self.path})'


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
