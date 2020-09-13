import os

from collections import defaultdict
from functools import cached_property

from pathlib import Path


class FileSet:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.site_assets = File(self.base_path, 'assets')
        self.site_build = File(self.base_path, 'build')

    def _file(self, name):
        file = File(self.base_path, name)
        return file if file.exists else NoFile()

    def _file_tree(self, name):
        base_path = self.base_path / name
        for path_str, _, files in os.walk(base_path):
            yield Path(path_str), files

    @property
    def config(self):
        return self._file('config.me')

    @property
    def templates(self):
        for path, files in self._file_tree('templates'):
            for file in files:
                yield File(path, file)

    @property
    def assets(self):
        for path, files in self._file_tree('assets'):
            for file in files:
                yield File(path, file)

    @property
    def data(self):
        for path, files in self._file_tree('data'):
            file = File(path, 'page.me')
            if file.exists:
                yield file  # DataFile


class File:
    def __init__(self, base_path, name):
        self.base_path = base_path
        self.path = base_path / name

    @property
    def name(self):
        return self.path.stem

    @property
    def type(self):
        return self.path.suffix.strip('.')

    @property
    def content(self):
        with open(self.path) as file:
            return file.read()

    @property
    def exists(self):
        return self.path.exists()

    def __repr__(self):
        return str(self.path)


class NoFile(File):
    @property
    def content(self):
        return f'File "{self.path}" not found'

    @property
    def exists(self):
        return False
