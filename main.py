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

from pathlib import PurePath

from sitegen import utils, site, reader
from sitegen.exceptions import (
    PageExistsError,
    TemplateError,
    PageValueError
)
from sitegen.filesystem import FileSystem


CONFIG_FILE = 'config.me'


def publish(args):
    '''Read recursively every directory under path and
    outputs a HTML for each page file'''
    path = PurePath(args.path)
    source_path = path / 'data'
    build_path = path / 'build'

    filesystem = FileSystem(source_path)

    config_string = filesystem.read_file(CONFIG_FILE)
    site_data = reader.parse(config_string)

    # fileset = filesystem.fileset()
    print(site_data)

    # for node in fileset:
    #     item = paging.read_page_file(node)

    # filesystem.write(item)

    # _site = site.Site(props)

    print("Success")
    # print("{}\nTotal of pages read: {}".format("-" * 30, len(pages)))


def main():
    description = 'A site generator'
    parser = argparse.ArgumentParser(prog='sitegen', description=description)

    subparsers = parser.add_subparsers(title='Commands', dest='command')
    subparsers.required = True

    parser_publish = subparsers.add_parser('publish', help='Generate HTML files')
    parser_publish.add_argument('path', nargs='?', default='.')
    parser_publish.set_defaults(method=publish)

    args = parser.parse_args()
    args.method(args)


if __name__ == '__main__':
    main()
