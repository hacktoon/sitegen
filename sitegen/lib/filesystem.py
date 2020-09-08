import os
from collections import defaultdict
from functools import cached_property
from pathlib import PurePath, Path

from .. import reader


DATA_FILE = 'page.me'


class PageArchive:
    def __init__(self, source_path):
        self.source_path = source_path
        self._path_hash = {
            str(pagefile.path) : pagefile
            for pagefile in self._filetree(source_path)
        }

    def __iter__(self):
        for pagefile in self._path_hash.values():
            yield pagefile

    def _filetree(self, source_path):
        for path_string, folders, files in os.walk(source_path):
            full_path = PurePath(path_string)
            page_path = full_path.relative_to(source_path)
            yield PageFile(full_path, page_path, folders, files)

    def get(self, path):
        pf = self._path_hash.get(path)
        print(pf)
        return self._path_hash.get(path)


class PageFile:
    def __init__(self, fullpath=PurePath(), path=PurePath(), folders=set(), files=set()):
        self.path = path
        self._fullpath = fullpath
        self._folders = set(folders)
        self._files = set(files)
        self._extensions = ExtensionMap(self._files)

    def files(self, extension=''):
        return self._extensions.get(extension, self._files)

    def folders(self):
        return self._folders

    @cached_property
    def data(self):
        file = self._fullpath / DATA_FILE
        print(file)
        return reader.parse(read_file(self._fullpath / DATA_FILE))

    def __repr__(self):
        return f'PageFile({self.path})'


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


class Page():
    def __init__(self):
        pass



def read_file(path):
    if not exists(path):
        return ''
    with open(path) as file:
        return file.read()


def exists(path):
    return Path(path).exists()