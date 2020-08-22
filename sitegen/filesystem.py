import os

from pathlib import PurePath

DATA_FILE = 'page.me'


class FileSystem:
    def __init__(self, basedir):
        self.nodes = [Node(*props) for props in os.walk(basedir)]

    def __iter__(self):
        for node in self.nodes:
            yield node


class Node:
    def __init__(self, path, folders, files):
        self.path = PurePath(path)
        self.folders = set(folders)
        self.files = set(files)

    @property
    def text(self):
        if not DATA_FILE in self.files:
            return ''
        file_path = self.path / DATA_FILE
        with open(file_path) as f:
            return f.read()

    @property
    def css(self):
        return []

    @property
    def js(self):
        return []

    def __repr__(self):
        return f'\n"{self.path}"'
        # return f'\n"{self.path}" - {self.data}'