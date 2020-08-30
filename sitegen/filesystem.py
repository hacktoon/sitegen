import os
from collections import defaultdict
from pathlib import PurePath, Path


class FileSystem:
    def __init__(self, base_path):
        self.base_path = base_path

    def exists(self, path):
        return Path(path).exists()

    def read_file(self, file_name):
        path = self.base_path / file_name
        if not self.exists(path):
            return ''
        with open(path) as file:
            return file.read()

    def fileset(self, data_path):
        return [
            FileSystemNode(path, files)
            for path, _, files in os.walk(data_path)
        ]


class FileSystemNode:
    def __init__(self, path, files):
        self.path = PurePath(path)
        self.file_names = set(files)
        self.extension_map = ExtensionMap(files)

    def read(self, filename, default=''):
        if not self.exists(filename):
            return default
        file_path = self.path / filename
        with open(file_path) as fp:
            return fp.read()

    def files(self, extension=''):
        return self.extension_map.get(extension, self.file_names)

    def exists(self, name):
        return name in self.file_names

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
