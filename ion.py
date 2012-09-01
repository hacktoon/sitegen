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
import json
import re
import sys
from datetime import datetime

# obey the rules
if sys.version_info.major < 3:
    sys.exit('Zap! Ion requires Python 3!')

# default template with all basic template variables
TEMPLATE_MODEL = '''<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8" />
        <link rel="stylesheet" href="{{themes_url}}bolt/main.css" type="text/css" />
        {{css}}
        <title>{{title}} | {{site_name}}</title>
    </head>
    <body>
        <h1><a href="{{base_url}}">{{site_name}}</a></h1>
        <p>{{site_description}}</p>
        <ul>
            <li><a href="{{base_url}}">Home</a></li>
            <li><a href="{{base_url}}about">About</a></li>
        </ul>
        <h2><a href="{{permalink}}">{{title}}</a></h2>
        <span>{{date}}</span>
        <p>{{content}}</p>
        {{js}}
    </body>
</html>
'''

# model of RSS file for feed generation
RSS_MODEL = '''<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
<channel>
    <title>{{site_name}}</title>
    <link>{{base_url}}</link>
    <description>{{description}}</description>
    {{item}}
</channel>
</rss>
'''
RSS_ITEM_MODEL = '''<item>
    <title>{{title}}</title>
    <link>{{permalink}}</link>
    <pubDate>{{date}}</pubDate>
    <description>{{content}}</description>
</item>
'''

# default configuration file
CONFIG_MODEL = '''#site name
site_name = My Ion site
# base_url must have a trailing slash
base_url = http://localhost/
# theme used by default if a custom theme is not provided in data files
default_theme = bolt
# directories Ion should not enter, comma separated
blocked_dirs = com, mydir, teste
'''

# this is the model of files used to store content
# it will be saved to a new file data.ion every
# time 'ion plug' is called
DATA_MODEL = '''title = Write your title here
date = {0}
content
Write your content here
'''

# pre-configuration values
CFG = {
    'system_dir': '_ion',
    'site_name': 'Ion',
    'site_description': 'An electric site.',
    'base_url': 'http://localhost/',
    'themes_dir': 'themes',
    'blocked_dirs': [],
    'template_file': 'main.tpl',
    'data_file': 'data.ion',
    'config_file': 'config.ion',
    'pagelog_file': 'pages.log',
    'default_theme': 'bolt',
    'rss_items': 8
}

def parse_ion_file(source_path):
    '''Parses *.ion data files and returns a dictionary'''
    data_file = open(source_path, 'r')
    page_data = {}
    while True:
        line = data_file.readline().strip()
        if line.startswith('#'):
            continue
        # if reached end of file, exit loop
        if len(line) == 0:
            break
        if(line == 'content'):
            # read the rest of the file
            key = line
            value = data_file.read()
        else:
            # will avoid splitting blank lines
            try:
                key, value = list(map(str.strip, line.split('=')))
            except:
                continue
        #setting values
        page_data[key] = value
    data_file.close()
    return page_data

def build_config():
    """Initializes config folder data"""
    CFG['system_path'] = os.path.join(os.getcwd(), CFG['system_dir'])
    CFG['config_path'] = os.path.join(CFG['system_path'], CFG['config_file'])
    CFG['themes_path'] = os.path.join(CFG['system_path'], CFG['themes_dir'])
    CFG['default_theme_path'] = os.path.join(CFG['themes_path'], CFG['default_theme'])
    CFG['default_template_path'] = os.path.join(CFG['default_theme_path'], CFG['template_file'])
    # adds an end slash to url if not provided
    CFG['themes_url'] = os.path.join(CFG['base_url'], CFG['system_dir'], CFG['themes_dir'], '')
    CFG['pagelog_path'] = os.path.join(CFG['system_path'], CFG['pagelog_file'])
    # Creates system folder
    if not os.path.exists(CFG['system_path']):
        print('Generating system folder {0}...'.format(CFG['system_path']))
        os.makedirs(CFG['system_path'])
    # Creates config file
    if not os.path.exists(CFG['config_path']):
        print('Generating config file {0}...'.format(CFG['config_path']))
        open(CFG['config_path'], 'w').write(CONFIG_MODEL)
    # Creating themes directory
    if not os.path.exists(CFG['themes_path']):
        os.makedirs(CFG['themes_path'])
    # Creating default theme directory
    if not os.path.exists(CFG['default_theme_path']):
        print('Generating default theme {0}...'.format(CFG['default_theme_path']))
        os.makedirs(CFG['default_theme_path'])
    # Creating default template file
    if not os.path.exists(CFG['default_template_path']):
        open(CFG['default_template_path'], 'w').write(TEMPLATE_MODEL)
    # Recent pages log file
    if not os.path.exists(CFG['pagelog_path']):
        open(CFG['pagelog_path'], 'w')

def load_config():
    '''Loads the config file in system folder'''
    build_config()
    config = parse_ion_file(CFG['config_path'])
    CFG['site_name'] = config.get('site_name', CFG['site_name'])
    # try to set a default value if it wasn't defined in config
    # add a trailing slash, if necessary
    CFG['base_url'] = os.path.join(config.get('base_url', CFG['base_url']), '')
    # get default theme, if it is defined in config
    CFG['default_theme'] = config.get('default_theme', CFG['default_theme'])
    # folders you don't want Ion to enter
    blocked = config.get('blocked_dirs')
    CFG['blocked_dirs'].append(CFG['system_dir'])
    for folder in blocked.split(','):
        CFG['blocked_dirs'].append(folder.strip())

def update_pagelog(path, date):
    '''Updates a log file containing list of all pages created'''
    if path == '.':
        return
    pageline = '{0} {1}\n'.format(path, date)
    open(CFG['pagelog_path'], 'a').write(pageline)

def has_data_file(path):
    data_file = os.path.join(path, CFG['data_file'])
    return os.path.exists(data_file)

def get_page_data(path):
    data_file = os.path.join(path, CFG['data_file'])
    # avoid directories that doesn't have a data file
    if not has_data_file(path):
        return
    page_data = parse_ion_file(data_file)
    # set common page data
    page_data['site_name'] = CFG['site_name']
    page_data['site_description'] = CFG['site_description']
    page_data['base_url'] = CFG['base_url']
    page_data['themes_url'] = CFG['themes_url']
    # if not using custom theme, use default
    page_data['theme'] = page_data.get('theme', CFG['default_theme'])
    # adds an end slash to url
    page_data['permalink'] = os.path.join(CFG['base_url'], path, '')
    return page_data

def fill_template(data, tpl):
    '''Replaces the variables in the template'''
    for key, value in data.items():
        regex = re.compile(r'\{\{\s*' + key + '\s*\}\}')
        tpl = re.sub(regex, value.strip(), tpl)
    return tpl

def build_external_tags(filenames, permalink, tag, ext):
    tag_list = []
    for filename in filenames.split(','):
        filename = filename.strip()
        url = os.path.join(permalink, filename)
        if filename.endswith(ext):
            tag_list.append(tag.format(url))
    return ''.join(tag_list)

def build_style_tags(filenames, permalink):
    tag = '<link rel="stylesheet" type="text/css" href="{0}" />\n'
    return build_external_tags(filenames, permalink, tag, '.css')

def build_script_tags(filenames, permalink):
    tag = '<script src="{0}"></script>\n'
    return build_external_tags(filenames, permalink, tag, '.js')

def save_json(dirname, page_data):
    json_filepath = os.path.join(dirname, 'index.json')
    json_file = open(json_filepath, 'w')
    json_file.write(json.dumps(page_data))
    json_file.close()

def save_html(path, page_data):
    theme_dir = os.path.join(CFG['themes_path'], page_data['theme'])
    tpl_filepath = os.path.join(theme_dir, CFG['template_file'])
    if not os.path.exists(tpl_filepath):
        sys.exit('Zap! Template file {0} couldn\'t be \
found!'.format(tpl_filepath))
    #abrindo arquivo de template e extraindo o html
    html_tpl = open(tpl_filepath, 'r').read()
    # get css and javascript found in the folder
    css = page_data.get('css', '')
    page_data['css'] = build_style_tags(css, page_data['permalink'])
    js = page_data.get('js', '')
    page_data['js'] = build_script_tags(js, page_data['permalink'])
    # fill template with page data
    html = fill_template(page_data, html_tpl)
    html_filepath = os.path.join(path, 'index.html')
    open(html_filepath, 'w').write(html)
    print('\'{0}\' generated.'.format(html_filepath))

def save_rss():
    pagelog = open(CFG['pagelog_path'], 'r').readlines()
    pagelog.reverse() # start from the newest
    for page in pagelog:
        path, date = page.split()
        if not has_data_file(path):
            continue


def ion_charge(path):
    '''Reads recursively every directory under path and
    outputs HTML/JSON for each data.ion file'''
    for dirpath, subdirs, filenames in os.walk(path):
        #removing '.' of the path in the case of root directory of site
        dirpath = re.sub('^\.$|\.\/', '', dirpath)
        if dirpath in CFG['blocked_dirs'] or not has_data_file(dirpath):
            continue
        page_data = get_page_data(dirpath)
        save_json(dirpath, page_data)
        save_html(dirpath, page_data)
    # after generating all pages, update feed
    save_rss()

def ion_plug(path):
    '''Creates a new page in specified path'''
    if not os.path.exists(path):
        os.makedirs(path)
    filepath = os.path.join(path, CFG['data_file'])
    if os.path.exists(filepath):
        print('Zap! Page \'{0}\' already exists \
with a data.ion file.'.format(path))
    else:
        date = datetime.now().strftime('%Y-%m-%d')
        # copy source file to new path
        data_file = open(filepath, 'w')
        data_file.write(DATA_MODEL.format(date))
        data_file.close()
        # saves data to file listing all pages created
        update_pagelog(path, date)
        print('Page \'{0}\' successfully created.'.format(path))
        print('Edit the file {0} and call \'ion charge\'!'.format(filepath))


if __name__ == '__main__':
    help_message = '''Usage:
    ion.py plug [path/to/folder] - Creates a empty page on path specified.
    ion.py charge [path/to/folder] - Generates HTML/JSON files of each \
folder under the path specified and its subfolders, recursively.
    ion.py help - Shows this help message.
    '''
    load_config()

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
        ion_plug(path)
    elif command == 'charge':
        ion_charge(path)
    elif command == 'help':
        sys.exit(help_message)
    else:
        print('Zap! {0} is a very strange command!'.format(command))
        sys.exit(help_message)
