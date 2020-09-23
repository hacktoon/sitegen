import os

from collections import defaultdict
from functools import cached_property

from pathlib import Path, PurePath


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
            namespace = self._namespace(root_path, path)
            yield path, namespace, filenames

    def _namespace(self, root_path, path):
        # data_path/namespace_path/file_path
        # return namespace as string
        relative_path = path.relative_to(root_path)
        return str(relative_path).replace('.', '')

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
        for path, _, filenames in self._filetree('data'):
            data_path = path / DataFile.FILENAME
            if not data_path.exists():
                continue
            file = self._build_file(path, filenames)
            yield file

    def _build_file(self, path, filenames):
        css = []
        js = []
        png = []
        for filename in filenames:
            asset = File(path, '', filename)
            if filename.endswith('.js'): js.append(asset)
            if filename.endswith('.css'): css.append(asset)
            if filename.endswith('.png'): png.append(asset)
        filemap = dict(css=css, js=js, png=png)
        return DataFile(path, filemap)


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
        return f'File({self.path})'


class DataFile(File):
    FILENAME = 'page.me'

    def __init__(self, base_path, filemap):
        super().__init__(base_path, '', self.FILENAME)

        self.css = filemap.get('css')
        self.js = filemap.get('js')
        self.png = filemap.get('png')

    def __repr__(self):
        return f'DataFile({self.path}, {self.css})'


class NoFile(File):
    def __init__(self):
        super().__init__(self, PurePath())

    @property
    def content(self):
        return ''

    def __repr__(self):
        return self.__class__.__name__