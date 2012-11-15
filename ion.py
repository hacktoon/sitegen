# coding: utf-8

'''
===============================================================================
Ion - A shocking simple static (site) generator

Author: Karlisson M. Bezerra
E-mail: contact@hacktoon.com
URL: https://github.com/karlisson/ion
License: WTFPL - http://sam.zoy.org/wtfpl/COPYING

===============================================================================
'''

import os
import sys
import re

import photon  # templating language
import quark  # low level module, basic bricks

# obey the rules
if sys.version_info.major < 3:
    sys.exit('Zap! Ion requires Python 3!')


def ion_charge(path):
    '''Reads recursively every directory under path and
    outputs HTML/JSON for each data.ion file'''
    config_check()
    config_load()
    for dirpath, subdirs, filenames in os.walk(path):
        #removing '.' of the path in the case of root directory of site
        dirpath = re.sub('^\.$|\.\/', '', dirpath)
        if not quark.has_data_file(dirpath):
            continue
        page_data = quark.get_page_data(dirpath)
        # get timestamp and convert to date format set in config
        page_data['date'] = quark.date_format(page_data['date'], \
            quark.CFG['date_format'])
        photon.save_json(dirpath, page_data)
        photon.save_html(dirpath, page_data)
    # after generating all pages, update feed
    photon.save_rss()


def ion_spark(path):
    '''Creates a new page in specified path'''
    #config_check()
    # copy source file to new path
    datafile_path = quark.create_page(path)
    # saves data to file listing all pages created
    quark.update_index(path)
    print('Page "{0}" successfully created!'.format(path))
    print('Edit the file "{0}" and call "ion charge"!'.format(datafile_path))


def ion_plug():
    '''Installs Ion in the current folder'''
    print('Installing Ion...')
    quark.create_site()
    sys.exit('\nIon is ready! Run "ion spark [path]" to create pages!\n')


def ion_help():
    help_message = '''Usage:
    ion.py plug - Installs Ion on this folder.
    ion.py spark [path/to/folder] - Creates a empty page on path specified.
    ion.py charge [path/to/folder] - Generates HTML/JSON files of each \
folder under the path specified and its subfolders, recursively.
    ion.py help - Shows this help message.
    '''
    sys.exit(help_message)

if __name__ == '__main__':
    # first parameter - command
    try:
        command = sys.argv[1]
    except IndexError:
        sys.exit(help_message)

    # second parameter - path
    # if not provided, defaults to current
    try:
        path = sys.argv[2]
    except IndexError:
        path = '.'

    if command == 'plug':
        ion_plug()
    elif command == 'spark':
        ion_spark(path)
    elif command == 'charge':
        ion_charge(path)
    elif command == 'help':
        ion_help()
    else:
        print('Zap! {0} is a very strange command!'.format(command))
        sys.exit(help_message)
