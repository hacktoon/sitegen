import os
from collections import defaultdict

from pathlib import PurePath


DATA_FILE = 'page.me'
COVER = 'image.png'


class FileSystem:
    def read(self, data_path):
        def build_node(folder_path, subfolder_names, file_names):
            base_path = PurePath(folder_path)
            subfolders = prepend_path(base_path, subfolder_names)
            files = prepend_path(base_path, file_names)
            fileset = FileSet(subfolders, files)
            return FSNode(base_path, fileset)

        def prepend_path(path, names):
            return [path / name for name in names]

        return [build_node(*params) for params in os.walk(data_path)]

    def __iter__(self):
        for folder in self.folders:
            yield folder


class FSNode:
    def __init__(self, base_path, fileset):
        # base_path ex: folder/data/
        # each file path in fileset is prefixed by base_path
        self.base_path = base_path
        self.fileset = fileset
        print(base_path, fileset.files)

    def read(self, paths):
        content = []
        for path in paths:
            with open(str(path)) as file:
                content.append(file.read())
        return '\n'.join(content)

    def files(self):
        return

    @property
    def data(self):
        return self.fileset.search('me')

    # @property
    # def cover(self):
    #     self.fileset.exists(COVER):
    #         return COVER
    #     return self.path.

    def __repr__(self):
        return f'\n"{self.path.relative}"'


class FileSet:
    def __init__(self, subfolders, files):
        self.extension_map = ExtensionMap(files)
        self.folders = subfolders
        self.files = files

    def exists(self, name):
        return name in self.files

    def search(self, name='', extension=''):
        return self.extension_map.get(extension)

    def __iter__(self):
        for file in self.folders:
            yield file


class ExtensionMap:
    def __init__(self, files):
        self._map = defaultdict(list)
        for file_path in files:
            ext = file_path.suffix.lower()
            self._map[ext].append(file_path)

    def get(self, extension):
        return self._map.get(extension, [])


class PathSet:
    def __init__(self, base_path, path):
        self.base_path = base_path
        self.full = PurePath(path)

    @property
    def base(self):
        return PurePath(self.base_path)

    @property
    def parent(self):
        return self.relative.parent

    @property
    def relative(self):
        return PurePath(self.full).relative_to(self.base_path)

    @property
    def folder(self):
        return self.relative.stem
