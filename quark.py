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
from collections import OrderedDict

import config


def url_join(start, end=''):
    start = start.strip('/')
    end = end.strip('/')
    url = '/'.join([start, end])
    if end:
        url += '/'
    return url


def read_file(path):
    if not os.path.exists(path):
        sys.exit('Zap! File "{0}" couldn\'t be \
found!'.format(path))
    with open(path, 'r') as f:
        return f.read()


def list_read_file(path):
    '''Reads a file and returns a list of its lines'''
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


def check_keys(keys, container, src):
    '''Checks for missing keys in a data container'''
    for key in keys:
        if not key in container:
            sys.exit('Zap! The key {!r} is missing in {!r}!'.format(key, src))


def extract_tags(tag_string):
    '''Converts a comma separated list of tags into a list'''
    tag_list = []
    if tag_string:
        tags = tag_string.strip(',').split(',')
        tag_list = [tag.strip() for tag in tags]
    return tag_list


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
    system_url = url_join(base_url, config.SITECONF_DIRNAME)
    return url_join(system_url, config.THEMES_DIRNAME)


def get_page_theme_dir(theme):
    '''Returns the folder path of the theme'''
    return os.path.join(get_themes_path(), theme)


def read_html_template(theme_name, tpl_filename):
    '''Returns a HTML template string from the current theme folder'''
    theme_dir = get_page_theme_dir(theme_name)
    if not tpl_filename.endswith('.tpl'):
        tpl_filename = '{0}.tpl'.format(tpl_filename)
    tpl_filepath = os.path.join(theme_dir, tpl_filename)
    if not os.path.exists(tpl_filepath):
        sys.exit('Zap! Template file "{0}" '
                 'couldn\'t be found!'.format(tpl_filepath))
    return read_file(tpl_filepath)


def read_rss_template():
    '''Returns a tuple containing the rss and rss items models'''
    data_dir = get_skeldata_dirpath()
    rss_filepath = os.path.join(data_dir, config.SKEL_RSS_FILENAME)
    return read_file(rss_filepath)


def get_pagedata_filepath(path):
    '''Returns the path of the data source file of a page'''
    return os.path.join(path, config.PAGE_DATA_FILENAME)


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
    content = read_file(src_path)
    # saving date in the format configured
    date = datetime.today()
    # need to write file contents to insert creation date
    write_file(dest_filepath, content.format(date))
    return dest_filepath


def get_page_collection(env):
    pages = {}
    # running at the current dir
    for dirpath, subdirs, filenames in os.walk('.'):
        page_data = get_page_data(env, dirpath)
        # if did not find a data file, ignores
        if page_data:
            pages[page_data['path']] = page_data
    # orders pages by date
    return sorted(pages.items(), key=lambda p: p[1]['date'])


def get_page_data(env, path):
    '''Returns a dictionary with the page data'''
    #removing '.' of the path in the case of root directory of site
    path = re.sub('^\.$|\./', '', path)
    data_file = get_pagedata_filepath(path)
    # avoid directories that doesn't have a data file
    if not os.path.exists(data_file):
        return
    page_data = parse_ion_file(data_file)
    # verify missing required keys in page data
    check_keys(['title', 'date', 'content'], page_data, data_file)
    # convert date string to datetime object
    date = page_data['date']
    try:
        page_data['date'] = datetime.strptime(date, config.DATE_FORMAT)
    except ValueError:
        sys.exit('Zap! Wrong date format detected at {!r}!'.format(data_file))
    # absolute link of the page
    page_data['permalink'] = url_join(env['base_url'], path)
    # if a theme is not provided, uses default
    page_data['theme'] = page_data.get('theme', env['default_theme'])
    # splits tags into a list
    page_data['tags'] = extract_tags(page_data.get('tags'))
    page_data['path'] = path
    return page_data


def get_env():
    '''Returns a dict containing the site data'''
    config_path = get_siteconf_filepath()
    env = parse_ion_file(config_path)
    # check for missing keys
    required_keys = ['site_name', 'site_author',
    'site_description', 'base_url', 'default_theme']
    check_keys(required_keys, env, config_path)
    # add a trailing slash to base url, if necessary
    base_url = url_join(env['base_url'])
    env['base_url'] = base_url
    env['themes_url'] = get_themes_url(base_url)
    env['feed_url'] = url_join(base_url, config.FEED_URL)
    env['site_tags'] = extract_tags(env.get('site_tags'))
    # now let's get all the pages
    env['pages'] = OrderedDict(get_page_collection(env))
    return env