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
import shutil
import time
from datetime import datetime
import config


def read_file(path):
    with open(path, 'r') as f:
        return f.read()


def list_read_file(path):
    with open(path, 'r') as f:
        return [l.strip() for l in f.readlines()]


def write_file(path, content='', append=False):
    mode = 'a' if append else 'w'
    with open(path, mode) as f:
        f.write(content)


def date_format(timestamp, fmt):
    '''helper to convert a timestamp into a given date format'''
    timestamp = float(timestamp)
    return datetime.fromtimestamp(timestamp).strftime(fmt)


def parse_ion_file(source_path):
    ion_data = {}
    lines = list_read_file(source_path)
    for num, line in enumerate(lines):
        # avoids empty lines and comments
        if not line or line.startswith('#'):
            continue
        if(line == config.CONTENT_KEY):
            # read the rest of the file
            ion_data[CONTENT_KEY] = ''.join(lines[num + 1:])
            break
        try:
            key, value = [l.strip() for l in line.split('=')]
            ion_data[key] = value
        except:
            continue
    return ion_data


def get_siteconf_dirpath():
    '''Returns the absolute path of the _ion config folder'''
    return os.path.join(os.getcwd(), config.SITECONF_DIRNAME)


def get_siteconf_filepath():
    '''Returns the absolute path of the config.ion file'''
    system_path = get_siteconf_dirpath()
    config_path = os.path.join(system_path, config.CONFIG_FILENAME)
    return config_path


def get_page_index():
    '''Returns the list of pages created'''
    system_path = get_siteconf_dirpath()
    index = os.path.join(system_path, config.INDEX_FILENAME)
    return list_read_file(index)


def get_themes_path():
    system_path = get_siteconf_dirpath()
    return os.path.join(system_path, config.THEMES_DIRNAME)


def get_themes_url(base_url):
    system_path = get_siteconf_dirpath()
    system_url = os.path.join(base_url, system_path)
    return os.path.join(system_url, config['themes_dir'], '')


def get_site_config():
    '''Returns a dict containing the current site config'''
    conf = {}
    config_path = get_siteconf_filepath()
    for key, value in parse_ion_file(config_path).items():
        conf[key] = value
    # add a trailing slash to base url, if necessary
    conf['base_url'] = os.path.join(config.get('base_url', ''), '')
    return conf


def get_pagedata_filepath(path):
    '''Returns the path of the data source file of a page'''
    return os.path.join(path, config.PAGE_DATA_FILENAME)


def get_skeldata_dirpath():
    '''get the skeleton data folder in the ion.py installation folder'''
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, config.SKEL_DATA_DIRNAME)


def create_site():
    script_datadir = get_skeldata_dirpath()
    # copying the skeleton _ion folder to new site folder
    orig_dir = os.path.join(script_datadir, config.SITECONF_DIRNAME)
    dest_dir = get_siteconf_dirpath()
    if os.path.exists(dest_dir):
        sys.exit('Zap! Ion is already installed in this folder!')
    print('Copying system config to "{0}"...'.format(dest_dir))
    shutil.copytree(orig_dir, dest_dir)


def create_page(path):
    if not os.path.exists(path):
        os.makedirs(path)
    dest_filepath = get_pagedata_filepath(path)
    if os.path.exists(dest_filepath):
        sys.exit('Zap! Page "{0}" already exists.'.format(path))
    # copy the skel page data file to new page
    src_path = get_pagedata_filepath(get_skeldata_dirpath())
    # saving timestamp
    date = time.mktime(datetime.now().timetuple())
    # need to write file contents to insert creation date
    write_file(dest_filepath, read_file(src_path).format(date))
    return dest_filepath


'''def config_check():
    #Runs diagnostics on the system
    system_path, config_path = quark.system_pathinfo()
    exit_msg = 'Run "ion plug" to install Ion in this folder!'
    errors_found = False
    if not os.path.exists(config_path):
        print('Zap! Ion config file doesn\'t exists!')
        sys.exit(exit_msg)
    # load config file to test its values
    config_load()
    themes_path = os.path.join(system_path, quark.CFG['themes_dir'])
    if not os.path.exists(themes_path):
        print('Zap! Themes folder doesn\'t exists!')
        errors_found = True
    dft_themepath = os.path.join(themes_path, quark.CFG['default_theme'])
    dft_tplpath = os.path.join(dft_themepath, quark.CFG['template_file'])
    # Checking default theme directory
    if not os.path.exists(dft_themepath):
        print('Zap! Default theme folder doesn\'t exists!')
        errors_found = True
    # Checking default template file
    if not os.path.exists(dft_tplpath):
        print('Zap! Default template file doesn\'t exists!')
        errors_found = True
    index_path = os.path.join(system_path, quark.CFG['index_file'])
    if not os.path.exists(index_path):
        print('Zap! Index file doesn\'t exists!')
        errors_found = True
    if errors_found:
        sys.exit(exit_msg)
'''

def update_index(path):
    '''Updates a log file containing list of all pages created'''
    if path == '.':
        return
    pageline = '{0}\n'.format(path)
    system_path = get_siteconf_dirpath()
    index_path = os.path.join(system_path, config.INDEX_FILENAME)
    write_file(index_path, pageline, append=True)


def has_data_file(path):
    data_file = os.path.join(path, CFG['data_file'])
    return os.path.exists(data_file)


def get_pagelist_preset(theme, name):
    path = os.path.join(CFG['themes_path'], theme, name + '.preset')
    if not os.path.exists(path):
        return DEFAULT_PAGELIST_PRESET
    return read_file(path)


def get_current_theme_dir(theme):
    return os.path.join(CFG['themes_path'], theme)


def get_page_data(path):
    data_file = get_pagedata_filepath(path)
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
