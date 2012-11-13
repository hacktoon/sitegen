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
from datetime import datetime


def read_file(path):
    with open(path, 'r') as f:
        return f.read()


def list_read_file(path):
    with open(path, 'r') as f:
        return [l.strip() for l in f.readlines()]


def write_file(path, content=''):
    with open(path, 'w') as f:
        f.write(content)


def append_file(path, content=''):
    with open(path, 'a') as f:
        f.write(content)


def date_format(timestamp, fmt):
    '''helper to convert a timestamp into a given date format'''
    timestamp = float(timestamp)
    return datetime.fromtimestamp(timestamp).strftime(fmt)


def parse_ion_file(source_path):
    ion_data = {}
    with open(source_path, 'r') as f:
        lines = f.readlines()
    for num, line in enumerate(lines):
        line = line.strip()
        # avoids empty lines and comments
        if not line or line.startswith('#'):
            continue
        if(line == 'content'):
            # read the rest of the file
            ion_data['content'] = ''.join(lines[num + 1:])
            break
        try:
            key, value = [l.strip() for l in line.split('=')]
            ion_data[key] = value
        except:
            continue
    return ion_data


def has_data_file(path):
    data_file = os.path.join(path, CFG['data_file'])
    return os.path.exists(data_file)


def system_pathinfo():
    system_path = os.path.join(os.getcwd(), CFG['system_dir'])
    config_path = os.path.join(system_path, CFG['config_file'])
    return system_path, config_path


def get_pagelist_preset(theme, name):
    path = os.path.join(CFG['themes_path'], theme, name + '.preset')
    if not os.path.exists(path):
        return DEFAULT_PAGELIST_PRESET
    return read_file(path)


def get_current_theme_dir(theme):
    return os.path.join(CFG['themes_path'], theme)


def get_page_index():
    return list_read_file(CFG['index_path'])


def get_page_data(path):
    data_file = os.path.join(path, CFG['data_file'])
    # avoid directories that doesn't have a data file
    if not has_data_file(path):
        return
    page_data = parse_ion_file(data_file)
    # set common page data
    page_data['site_name'] = CFG['site_name']
    page_data['site_author'] = CFG['site_author']
    page_data['site_description'] = CFG['site_description']
    page_data['base_url'] = CFG['base_url']
    page_data['themes_url'] = CFG['themes_url']
    # if not using custom theme, use default
    page_data['theme'] = page_data.get('theme', CFG['default_theme'])
    # adds an end slash to url
    page_data['permalink'] = os.path.join(CFG['base_url'], path, '')
    return page_data
