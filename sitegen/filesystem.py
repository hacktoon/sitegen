import os
from collections import defaultdict

from pathlib import PurePath


DATA_FILE = 'page.me'


class FileSystem:
    def __init__(self, base_path):
        self.base_path = base_path
        self.nodes = []
        for path, folders, files in os.walk(base_path):
            fileset = Fileset(folders, files)
            node = Node(path, fileset)
            self.nodes.append(node)

    def __iter__(self):
        for node in self.nodes:
            yield node


class Node:
    def __init__(self, path, fileset):
        self.path = PurePath(path)
        self.fileset = fileset

    @property
    def data(self):
        full_data = []
        for me_file in self.fileset.files('me'):
            file_path = self.path / me_file
            with open(file_path) as f:
                full_data.append(f.read())
        return '\n'.join(full_data)

    @property
    def css(self):
        return self.fileset.files('css')

    @property
    def js(self):
        return self.fileset.files('js')

    def __repr__(self):
        return f'\n"{self.path}"'
        # return f'\n"{self.path}" - {self.data}'


class Fileset:
    def __init__(self, folder_list, file_list):
        self.folder_list = folder_list
        self.file_list = file_list
        self.extension_dict = extension_dict(file_list)

    def files(self, extension=None):
        if extension is None:
            return self.file_list
        return self.extension_dict[extension]


def extension_dict(file_list):
    ext_dict = defaultdict(list)
    for file_name in file_list:
        ext = file_extension(file_name)
        ext_dict[ext].append(file_name)
    return ext_dict


def file_extension(file_name):
    *_, ext = file_name.split('.')
    return ext.lower()
