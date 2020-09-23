# coding: utf-8

'''
===============================================================================
Sitegen

Author: Karlisson M. Bezerra
E-mail: contact@hacktoon.com
URL: https://github.com/hacktoon/sitegen
License: WTFPL - http://sam.zoy.org/wtfpl/COPYING
===============================================================================
'''

import argparse
import sys
import os

from sitegen.exceptions import (
    PageExistsError,
    TemplateError,
    PageValueError
)
from sitegen.filesystem import FileSet
from sitegen.lib import URL


def generate(args):
    url = URL('http://localhost:8080')

    # Get file structure
    # read/build config Files
    fileset = FileSet(args.input)
    print(list(fileset.data))


def main():
    description = 'A site generator'
    parser = argparse.ArgumentParser(prog='sitegen', description=description)

    subparsers = parser.add_subparsers(title='Commands', dest='command')
    subparsers.required = True

    parser_publish = subparsers.add_parser('publish', help='Generate HTML files')
    parser_publish.add_argument('input', nargs='?', default='')
    parser_publish.set_defaults(method=generate)

    args = parser.parse_args()
    args.method(args)


if __name__ == '__main__':
    main()
