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


def urljoin(base, slug):
    '''Custom URL join function to concatenate and add slashes'''
    return '/'.join(s.strip('/') for s in [base, slug])


def read_file(path):
    if not os.path.exists(path):
        sys.exit('Zap! File {!r} couldn\'t be found!'.format(path))
    with open(path, 'r') as f:
        return f.read()


def write_file(path, content=''):
    with open(path, 'w') as f:
        f.write(content)


def parse_ion_file(file_string):
    ion_data = {}
    lines = file_string.split('\n')
    for num, line in enumerate(lines):
        # avoids empty lines and comments
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if(line == 'content'):
            # read the rest of the file
            ion_data['content'] = ''.join(lines[num + 1:])
            break
        key, value = [l.strip() for l in line.split('=', 1)]
        ion_data[key] = value
    return ion_data


def check_keys(keys, container, src):
    '''Checks for missing keys in a data container'''
    for key in keys:
        if not key in container:
            raise Exception('Zap! The key {!r} '
            'is missing in {!r}!'.format(key, src))
    return True


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


def get_themes_url(base_url):
    '''Returns the URL of the themes folder'''
    return urljoin(base_url, config.THEMES_DIRNAME)


def get_page_theme_dir(theme):
    '''Returns the folder path of the theme'''
    system_path = find_siteconf_dir()
    theme_path= os.path.join(system_path, config.THEMES_DIRNAME)
    return os.path.join(theme_path, theme)


def read_html_template(theme_name, tpl_filename):
    '''Returns a HTML template string from the current theme folder'''
    theme_dir = get_page_theme_dir(theme_name)
    if not tpl_filename.endswith('.tpl'):
        tpl_filename = '{0}.tpl'.format(tpl_filename)
    tpl_filepath = os.path.join(theme_dir, tpl_filename)
    if not os.path.exists(tpl_filepath):
        sys.exit('Zap! Template file {!r} '
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
    if get_siteconf_path():
        sys.exit('Zap! Ion is already installed in this folder!')
    # get the model _ion folder
    script_datadir = get_skeldata_dirpath()
    # copying the skeleton _ion folder to new site folder
    orig_dir = script_datadir
    dest_dir = os.getcwd()
    print('Copying system config to {!r}...'.format(dest_dir))
    shutil.copytree(orig_dir, dest_dir)


def create_page(path):
    '''Creates a data.ion file in the folder passed as parameter'''
    if not find_siteconf_dir():
        sys.exit('Zap! Ion is not installed in this folder!')
    if not os.path.exists(path):
        os.makedirs(path)
    # full path of page data file
    dest_filepath = get_pagedata_filepath(path)
    if os.path.exists(dest_filepath):
        sys.exit('Zap! Page {!r} already exists.'.format(path))
    # copy the skel page data file to new page
    src_path = get_pagedata_filepath(get_skeldata_dirpath())
    content = read_file(src_path)
    # saving date in the format configured
    date = datetime.today().strftime(config.DATE_FORMAT)
    # need to write file contents to insert creation date
    write_file(dest_filepath, content.format(date))
    return dest_filepath


def get_page_data(env, path):
    '''Returns a dictionary with the page data'''
    #removing '.' of the path in the case of root directory of site
    data_file = get_pagedata_filepath(path)
    # avoid directories that doesn't have a data file
    if not os.path.exists(data_file):
        return
    page_data = parse_ion_file(read_file(data_file))
    # verify missing required keys in page data
    check_keys(['title', 'date', 'content'], page_data, data_file)
    # convert date string to datetime object
    date = page_data['date']
    try:
        page_data['date'] = datetime.strptime(date, config.DATE_FORMAT)
    except ValueError:
        sys.exit('Zap! Wrong date format detected at {!r}!'.format(data_file))
    # absolute link of the page
    page_data['permalink'] = urljoin(env['base_url'], path)
    # if a theme is not provided, uses default
    page_data['theme'] = page_data.get('theme', env['default_theme'])
    # splits tags into a list
    page_data['tags'] = extract_tags(page_data.get('tags'))
    page_data['path'] = path
    return page_data


def read_page_files(env):
    '''Returns all the pages created in the site'''
    pages = {}
    # running at the current dir
    for path, subdirs, filenames in os.walk(env['config_dir']):
        # if did not find a data file, ignores  
        if not config.PAGE_DATA_FILENAME in filenames:
            continue
        path = re.sub('^\.$|\./', '', path)
        page_data = get_page_data(env, path)
        page_data['children'] = []
        if path: # checks if isnt home page
            # get parent folder to include itself as child page
            parent_path = os.path.dirname(path)
            # linking children pages, only if parent exists
            if parent_path in pages:
                pages[parent_path]['children'].append(page_data)
        # uses the page path as a key
        pages[page_data['path']] = page_data
    return pages


def get_env():
    '''Returns a dict containing the site data'''
    config_dir = find_siteconf_dir()
    if not config_dir:
        sys.exit('Zap! Ion is not installed in this folder!')
    config_path = os.path.join(config_dir, config.CONFIG_FILENAME)
    env = parse_ion_file(read_file(config_path))
    # check for missing keys
    required_keys = ['site_name', 'site_author',
    'site_description', 'base_url', 'default_theme']
    check_keys(required_keys, env, config_path)
    # add a trailing slash to base url, if necessary
    base_url = urljoin(env['base_url'], '/')
    env['config_dir'] = config_dir
    env['base_url'] = base_url
    env['themes_url'] = get_themes_url(base_url)
    env['feed_url'] = urljoin(base_url, config.FEED_URL)
    env['site_tags'] = extract_tags(env.get('site_tags'))
    # now let's get all the pages
    env['pages'] = read_page_files(env)
    return env


def dataset_filter_category(dataset, cat=None):
    # FIXME - this may not work on windows - path/slug
    if not cat:
        return dataset
    from_cat = lambda c: c['path'].startswith(cat)
    dataset = [page for page in dataset if from_cat(page)]
    return dataset


def dataset_sort(dataset, sort, order):
    reverse = (order == 'desc')
    sort_by = lambda d: d[sort or 'date']
    return sorted(dataset, key=sort_by, reverse=reverse)


def dataset_range(dataset, num_range):
    if not dataset or not num_range:
        return dataset
    # limit number of objects to show
    start, end = num_range.partition(':')[::2]
    try:
        start = abs(int(start)) if start else 0
        end = abs(int(end)) if end else None
    except ValueError:
        sys.exit('Zap! Bad range argument!')
    if ':' in num_range:
        return dataset[start:end]
    else: # a single number means quantity of posts
        return dataset[:start]


def query_pages(env, page, dataset, args=None):
    if not dataset:
        return dataset
    # limit the category first
    dataset = dataset_filter_category(dataset, args.get('cat'))
    # listing order before number of objects
    dataset = dataset_sort(dataset, args.get('sort'), args.get('ord'))
    # number must be the last one
    dataset = dataset_range(dataset, args.get('num'))
    return dataset


def query(env, page, args):
    '''Make queries to the environment data set'''
    # get the source argument
    src = args.get('src', '')
    sources = {
        'pages': [query_pages, list(env['pages'].copy().values())],
        'children': [query_pages, page.get('children', [])[:]]
    }
    # calling the proper query function
    if src in sources:
        dataset = sources[src][1]
        return sources[src][0](env, page, dataset, args)
    else:
        sys.exit('Zap! "src" argument is'
        ' missing or invalid!'.format(src))
