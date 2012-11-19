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
import shutil
import time
from datetime import datetime
import config


def read_file(path):
    if not os.path.exists(path):
        sys.exit('Zap! File "{0}" couldn\'t be \
found!'.format(path))
    with open(path, 'r') as f:
        return f.read()


def list_read_file(path):
    if not os.path.exists(path):
        sys.exit('Zap! File "{0}" couldn\'t be \
found!'.format(path))
    with open(path, 'r') as f:
        return [l.strip() for l in f.readlines()]


def write_file(path, content='', append=False):
    mode = 'a' if append else 'w'
    with open(path, mode) as f:
        f.write(content)


def parse_ion_file(source_path):
    ion_data = {}
    lines = list_read_file(source_path)
    for num, line in enumerate(lines):
        # avoids empty lines and comments
        if not line or line.startswith('#'):
            continue
        if(line == config.CONTENT_KEY):
            # read the rest of the file
            ion_data[config.CONTENT_KEY] = ''.join(lines[num + 1:])
            break
        try:
            key, value = [l.strip() for l in line.split('=')]
            ion_data[key] = value
        except:
            continue
    return ion_data


def get_skeldata_dirpath():
    '''Gets the skeleton data folder in the Ion installation folder'''
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, config.SKEL_DATA_DIRNAME)


def get_siteconf_dirpath():
    '''Returns the absolute path of the _ion config folder'''
    return os.path.join(os.getcwd(), config.SITECONF_DIRNAME)


def get_siteconf_filepath():
    '''Returns the absolute path of the config.ion file'''
    system_path = get_siteconf_dirpath()
    config_path = os.path.join(system_path, config.CONFIG_FILENAME)
    return config_path


def get_themes_path():
    '''Returns the path of the themes folder'''
    system_path = get_siteconf_dirpath()
    return os.path.join(system_path, config.THEMES_DIRNAME)


def get_themes_url(base_url):
    '''Returns the URL of the themes folder'''
    system_url = os.path.join(base_url, config.SITECONF_DIRNAME)
    return os.path.join(system_url, config.THEMES_DIRNAME, '')


def get_page_theme_dir(theme):
    '''Returns the folder path of the theme'''
    return os.path.join(get_themes_path(), theme)


def read_html_template(theme_name):
    '''Returns a HTML template string from the current theme folder'''
    theme_dir = get_page_theme_dir(theme_name)
    tpl_filepath = os.path.join(theme_dir, config.THEMES_MAIN_TEMPL)
    if not os.path.exists(tpl_filepath):
        sys.exit('Zap! Template file "{0}" couldn\'t be \
found!'.format(tpl_filepath))
    return read_file(tpl_filepath)


def read_rss_templates():
    '''Returns a tuple containing the rss and rss items models'''
    data_dir = get_skeldata_dirpath()
    rss_filepath = os.path.join(data_dir, config.SKEL_RSS_FILENAME)
    rssitem_filepath = os.path.join(data_dir, config.SKEL_RSSITEM_FILENAME)
    return (read_file(rss_filepath), read_file(rssitem_filepath))


def get_pagedata_filepath(path):
    '''Returns the path of the data source file of a page'''
    return os.path.join(path, config.PAGE_DATA_FILENAME)


def get_site_config():
    '''Returns a dict containing the current site config'''
    config_path = get_siteconf_filepath()
    site_config = parse_ion_file(config_path)
    # add a trailing slash to base url, if necessary
    site_config['base_url'] = os.path.join(site_config.get('base_url', ''), '')
    site_config['themes_url'] = get_themes_url(site_config['base_url'])
    return site_config


def get_page_data(path):
    '''Returns a dictionary with the page data'''
    #removing '.' of the path in the case of root directory of site
    path = re.sub('^\.$|\.\/', '', path)
    data_file = get_pagedata_filepath(path)
    # avoid directories that doesn't have a data file
    if not os.path.exists(data_file):
        return {}
    page_data = parse_ion_file(data_file)
    site_config = get_site_config()
    # set common page data
    config_keys = ['site_name', 'site_author', 'site_description',
    'base_url', 'themes_url']
    for key in config_keys:
        page_data[key] = site_config.get(key, '')
    # if not using custom theme, use default
    default_theme = site_config.get('default_theme')
    page_data['theme'] = page_data.get('theme', default_theme)
    page_data['permalink'] = os.path.join(page_data['base_url'], path)
    return page_data


def update_index(path):
    '''Updates a log file containing list of all pages created'''
    if path == '.':
        return
    entry = '{0}\n'.format(path)
    system_path = get_siteconf_dirpath()
    index_path = os.path.join(system_path, config.INDEX_FILENAME)
    write_file(index_path, entry, append=True)


def get_page_index():
    '''Returns the list of pages created'''
    system_path = get_siteconf_dirpath()
    index = os.path.join(system_path, config.INDEX_FILENAME)
    return list_read_file(index)


def create_site():
    '''Copies the skel _ion folder to the current dir'''
    script_datadir = get_skeldata_dirpath()
    # copying the skeleton _ion folder to new site folder
    orig_dir = os.path.join(script_datadir, config.SITECONF_DIRNAME)
    dest_dir = get_siteconf_dirpath()
    if os.path.exists(dest_dir):
        sys.exit('Zap! Ion is already installed in this folder!')
    print('Copying system config to "{0}"...'.format(dest_dir))
    shutil.copytree(orig_dir, dest_dir)


def create_page(path):
    '''Creates a data.ion file in the folder passed as parameter'''
    if not os.path.exists(path):
        os.makedirs(path)
    # full path of page data file
    dest_filepath = get_pagedata_filepath(path)
    if os.path.exists(dest_filepath):
        sys.exit('Zap! Page "{0}" already exists.'.format(path))
    # copy the skel page data file to new page
    src_path = get_pagedata_filepath(get_skeldata_dirpath())
    site_config = get_site_config()
    # saving date in the format configured
    date = datetime.today().strftime(site_config['date_format'])
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
