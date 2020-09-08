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

from sitegen import utils, site
from sitegen.paging import PageBuilder
from sitegen.exceptions import (
    PageExistsError,
    TemplateError,
    PageValueError
)
from sitegen.lib.filesystem import PageArchive
from sitegen.lib import URL


SITE_CONFIG_FILE = 'config.me'
PAGE_CONFIG_FILE = 'page.me'  # change to content.txt


def publish(args):
    base_url = URL('http://localhost:8080')


def generate(args):
    '''Read recursively every directory under path and
    outputs a HTML for each page file'''
    path = PurePath(args.path)
    source_path = path / 'data'

    # config_string = input_fs.read_file(source_path / SITE_CONFIG_FILE)
    # site_config = reader.parse(config_string)

    archive = PageArchive(source_path)
    print(archive.get('posts/2011/pale-blue-dot').data)

    # build page map
    # _site = site.Site(site_config, pages)
    # filesystem.write(item)

    print("---\nDone")
    # print("{}\nTotal of pages read: {}".format("-" * 30, len(pages)))


def main():
    description = 'A site generator'
    parser = argparse.ArgumentParser(prog='sitegen', description=description)

    subparsers = parser.add_subparsers(title='Commands', dest='command')
    subparsers.required = True

    parser_publish = subparsers.add_parser('publish', help='Generate HTML files')
    parser_publish.add_argument('path', nargs='?', default='.')
    parser_publish.set_defaults(method=generate)

    args = parser.parse_args()
    args.method(args)


if __name__ == '__main__':
    main()
