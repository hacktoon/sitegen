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

from sitegen import utils, site, reader
from sitegen.exceptions import (
    PageExistsError,
    TemplateError,
    PageValueError
)


CONFIG_FILE = 'config.me'


def publish(args):
    '''Read recursively every directory under path and
    outputs a HTML for each page file'''
    path = args.path

    config_path = os.path.join(path, CONFIG_FILE)
    if not os.path.exists(config_path):
        print('No site.')
        return
    config_file = utils.read_file(config_path)
    try:
        props = reader.parse(config_file)
    except PageValueError as err:
        raise PageValueError('File {!r}: {}'.format(config_path, err))
    _site = site.Site(props)

    try:
        pages = _site.publish_pages(path)
    except (FileNotFoundError, ValueError,
            TemplateError, PageValueError) as e:
        sys.exit(e)
    print("{}\nTotal of pages read: {}".format("-" * 30, len(pages)))


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
