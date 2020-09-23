import os

from collections import defaultdict
from functools import cached_property

from pathlib import Path, PurePath


DATA_FILE = 'page.me'


class FileSet:
    def __init__(self, base_path):
        self.base_path = Path(base_path)

    def _file(self, name):
        file = File(self.base_path, '', name)
        return file if file.exists else NoFile()

    def _filetree(self, name, suffix=''):
        root_path = self.base_path / name
        for path_str, _, _filenames in os.walk(root_path):
            filenames = [name for name in _filenames if name.endswith(suffix)]
            path = Path(path_str)
            namespace = str(path.relative_to(root_path)).replace('.', '')
            yield path, namespace, filenames

    @property
    def config(self):
        return self._file('config.me')

    @property
    def templates(self):
        for path, namespace, filenames in self._filetree('templates', '.tpl'):
            for filename in filenames:
                yield File(path, namespace, filename)

    @property
    def assets(self):
        for path, namespace, filenames in self._filetree('assets'):
            for filename in filenames:
                yield File(path, namespace, filename)

    @property
    def data(self):
        for path, files in self._filetree('data'):
            data_path = path / DATA_FILE
            if data_path.exists():
                css = path.glob('*.css')
                js = path.glob('*.js')
                yield list(css)


class File:
    def __init__(self, base_path, namespace='', filename=''):
        self.path = base_path / namespace / filename
        self.namespace = namespace
        self.filename = filename

    @property
    def name(self):
        return PurePath(self.filename).stem

    @property
    def type(self):
        return PurePath(self.filename).suffix.lstrip('.')

    @property
    def content(self):
        with open(self.path) as file:
            return file.read()

    def __repr__(self):
        return str(self.path)


class DataFile(File):
    def __init__(self, base_path, data_file, files):
        super().__init__(self, base_path, name)


class NoFile(File):
    def __init__(self):
        super().__init__(self, PurePath())

    @property
    def content(self):
        return ''

    def __repr__(self):
        return self.__class__.__name__