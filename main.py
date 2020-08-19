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

from sitegen import utils, site
from sitegen.exceptions import (
    PageExistsError,
    SiteAlreadyInstalledError,
    TemplateError,
    PageValueError
)


def publish(args):
    '''Read recursively every directory under path and
    outputs HTML/JSON for each page file'''
    path = args.path
    _site = site.Site()
    try:
        _site.enter(path)
    except FileNotFoundError:
        sys.exit('No library were ever built in {!r}.'.format(path))
    except PageValueError as err:
        sys.exit(err)

    try:
        pages = _site.publish_pages(path)
    except (FileNotFoundError, ValueError,
            TemplateError, PageValueError) as e:
        sys.exit(e)
    if args.verbose:
        print("{}\nTotal of pages read: {}.".format("-" * 30, len(pages)))


def write(args):
    '''Create a new page in specified path'''
    path = utils.clear_path(args.path)
    _site = site.Site()
    try:
        _site.enter(path)
    except FileNotFoundError:
        sys.exit('No library were ever built in {!r}.'.format(path))
    try:
        _site.write_page(path)
    except PageExistsError as e:
        sys.exit(e)

    print('Page {!r} successfully created!'.format(path))
    print('Edit the file {}/page.me and call "sitegen build"!'.format(path))


def build(args):
    '''Build site in the current path'''
    print('Building site...')

    _site = site.Site()
    try:
        _site.build(os.curdir)
    except SiteAlreadyInstalledError as e:
        sys.exit(e)

    print('\nSite was successfully installed!\n\n'
    'Next steps:\n1 - Edit the "config.me" file.\n'
    '2 - Run "sitegen write [path]" to start creating pages!\n')


def main():
    description = 'The Infinite Automaton Scriber of Nimus Ages'
    parser = argparse.ArgumentParser(prog='sitegen',
	                                 description=description)

    parser.add_argument("-v", "--verbose",
                        help="show generation messages",
                        action="store_true")

    parser.add_argument("-x", "--update-cache",
                        help="update the template and page caches",
                        action="store_true")

    subparsers = parser.add_subparsers(title='Commands', dest='command')
    subparsers.required = True

    parser_build = subparsers.add_parser('build',
        help='build Sitegen on current folder')
    parser_build.set_defaults(method=build)

    parser_write = subparsers.add_parser('write',
        help='create a empty page on the path specified')
    parser_write.add_argument('path')
    parser_write.set_defaults(method=write)

    parser_publish = subparsers.add_parser('publish', help='generate the pages')
    parser_publish.add_argument('path', nargs='?', default='.')
    parser_publish.set_defaults(method=publish)

    args = parser.parse_args()
    args.method(args)

if __name__ == '__main__':
    main()
