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
import json
import time
from datetime import datetime

# obey the rules
if sys.version_info.major < 3:
    sys.exit('Zap! Ion requires Python 3!')

# default template with all basic template variables
TEMPLATE_MODEL = '''<!DOCTYPE html>
<html>
<head>
    <meta name="author" content="{{site_author}}" />
    <meta name="description" content="{{site_description}}" />
    <meta name="keywords" content="{{tags}}" />
    <meta charset="UTF-8" />
    <link rel="stylesheet" href="{{themes_url}}bolt/ion.css" type="text/css" />
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
    <p>{{pages:3}}</p>
    {{js}}
</body>
</html>
'''

# model of RSS file for feed generation
RSS_MODEL = '''<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0"
    xmlns:atom="http://www.w3.org/2005/Atom"
>
<channel>
    <title>{{site_name}}</title>
    <atom:link href="{{link}}rss.xml" rel="self" type="application/rss+xml" />
    <link>{{link}}</link>
    <description>{{description}}</description>
    <lastBuildDate>{{build_date}}</lastBuildDate>
    {{items}}
</channel>
</rss>
'''
RSS_ITEM_MODEL = '''
    <item>
        <title>{{title}}</title>
        <link>{{permalink}}</link>
        <pubDate>{{date}}</pubDate>
        <description><![CDATA[{{content}}]]></description>
        <guid>{{permalink}}</guid>
    </item>'''

# this is the model of files used to store content
# it will be saved to a new file data.ion every
# time 'ion plug' is called
DATA_MODEL = '''title = Write your title here
date = {0}
tags = proton, neutron, electron
content
Write your content here
'''

# customizable configuration values
CFG_MODEL = '''# main config file
site_name = My Ion site
site_author = Electric Joe
site_description = An electric site
base_url = http://localhost/
default_theme = bolt
# max number of items to list in RSS feed
rss_items = 8
# dd/mm/yyyy
date_format = %d/%m/%Y
utc_offset = +0000
'''

# system config values
CFG = {
    'system_dir': '_ion',
    'config_file': 'config.ion',
    'template_file': 'main.tpl',
    'data_file': 'data.ion',
    'index_file': 'index.log',
    'themes_dir': 'themes'
}


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
            key, value = list(map(str.strip, line.split('=')))
            ion_data[key] = value
        except:
            continue
    return ion_data


def system_pathinfo():
    system_path = os.path.join(os.getcwd(), CFG['system_dir'])
    config_path = os.path.join(system_path, CFG['config_file'])
    return system_path, config_path


def config_check():
    '''Runs diagnostics on the system'''
    system_path, config_path = system_pathinfo()
    exit_msg = 'Run "ion plug" to install Ion in this folder!'
    errors_found = False
    if not os.path.exists(config_path):
        print('Zap! Ion config file doesn\'t exists!')
        sys.exit(exit_msg)
    # load config file to test its values
    config_load()
    themes_path = os.path.join(system_path, CFG['themes_dir'])
    if not os.path.exists(themes_path):
        print('Zap! Themes folder doesn\'t exists!')
        errors_found = True
    dft_themepath = os.path.join(themes_path, CFG['default_theme'])
    dft_tplpath = os.path.join(dft_themepath, CFG['template_file'])
    # Checking default theme directory
    if not os.path.exists(dft_themepath):
        print('Zap! Default theme folder doesn\'t exists!')
        errors_found = True
    # Checking default template file
    if not os.path.exists(dft_tplpath):
        print('Zap! Default template file doesn\'t exists!')
        errors_found = True
    index_path = os.path.join(system_path, CFG['index_file'])
    if not os.path.exists(index_path):
        print('Zap! Index file doesn\'t exists!')
        errors_found = True
    if errors_found:
        sys.exit(exit_msg)


def config_load():
    '''Loads the config file in system folder'''
    system_path, config_path = system_pathinfo()
    for key, value in parse_ion_file(config_path).items():
        CFG[key] = value
    # add a trailing slash to base url, if necessary
    CFG['base_url'] = os.path.join(CFG['base_url'], '')
    system_url = os.path.join(CFG['base_url'], CFG['system_dir'])
    CFG['themes_url'] = os.path.join(system_url, CFG['themes_dir'], '')
    CFG['themes_path'] = os.path.join(system_path, CFG['themes_dir'])
    CFG['index_path'] = os.path.join(system_path, CFG['index_file'])


def date_format(timestamp, fmt):
    '''helper to convert a timestamp into a given date format'''
    timestamp = float(timestamp)
    return datetime.fromtimestamp(timestamp).strftime(fmt)


def update_index(path):
    '''Updates a log file containing list of all pages created'''
    if path == '.':
        return
    pageline = '{0}\n'.format(path)
    with open(CFG['index_path'], 'a') as f:
        f.write(pageline)


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
    page_data['site_author'] = CFG['site_author']
    page_data['site_description'] = CFG['site_description']
    page_data['base_url'] = CFG['base_url']
    page_data['themes_url'] = CFG['themes_url']
    # if not using custom theme, use default
    page_data['theme'] = page_data.get('theme', CFG['default_theme'])
    # adds an end slash to url
    page_data['permalink'] = os.path.join(CFG['base_url'], path, '')
    return page_data


def fill_template(variables, tpl):
    '''Replaces the page variables in the given template'''
    # gets the last pages
    index = []
    with open(CFG['index_path'], 'r') as f:
        index = f.readlines()
    # first replace the variables
    for key, value in variables.items():
        tag_re = re.compile(r'\{\{\s*' + key + '\s*\}\}')
        tpl = re.sub(tag_re, value.strip(), tpl)
    # include fragments
    # page listings
    page_re = re.compile(r'\{\{\s*pages:(?P<num_pages>\d+)\s*\}\}')
    for number in re.findall(page_re, tpl):
        page_list = index[:int(number)]
        list_re = re.compile(r'\{\{\s*pages:'+number+'\s*\}\}')
        tpl = re.sub(list_re, '\n'.join(page_list), tpl);
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
    with open(json_filepath, 'w') as f:
        f.write(json.dumps(page_data))


def save_html(path, page_data):
    theme_dir = os.path.join(CFG['themes_path'], page_data['theme'])
    tpl_filepath = os.path.join(theme_dir, CFG['template_file'])
    if not os.path.exists(tpl_filepath):
        sys.exit('Zap! Template file {0} couldn\'t be \
found!'.format(tpl_filepath))
    #abrindo arquivo de template e extraindo o html
    with open(tpl_filepath, 'r') as f:
        html_tpl = f.read()
    # get css and javascript found in the folder
    css = page_data.get('css', '')
    page_data['css'] = build_style_tags(css, page_data['permalink'])
    js = page_data.get('js', '')
    page_data['js'] = build_script_tags(js, page_data['permalink'])
    # fill template with page data
    html = fill_template(page_data, html_tpl)
    with open(os.path.join(path, 'index.html'), 'w') as f:
        f.write(html)
    print('\'{0}\' generated.'.format(path))


def save_rss():
    rss_data = {}
    with open(CFG['index_path'], 'r') as f:
        index = f.readlines()
    if not len(index):
        return
    rss_data['site_name'] = CFG['site_name']
    rss_data['link'] = CFG['base_url']
    rss_data['description'] = CFG['site_description']
    items = []
    # will get only the first n items
    max_items = int(CFG['rss_items'])
    for page in index[:max_items]:
        page = page.strip()  # remove newlines
        if not has_data_file(page):
            continue
        page_data = get_page_data(page)
        # get timestamp and convert to rfc822 date format
        rfc822_fmt = '%a, %d %b %Y %H:%M:%S ' + CFG['utc_offset']
        page_data['date'] = date_format(page_data['date'], rfc822_fmt)
        # get last page date to fill lastBuildDate
        rss_data['build_date'] = page_data['date']
        items.append(fill_template(page_data, RSS_ITEM_MODEL))
    items.reverse()  # the last inserted must be the first in rss
    rss_data['items'] = '\n'.join(items)
    rss = fill_template(rss_data, RSS_MODEL)
    with open('rss.xml', 'w') as f:
        f.write(rss)


def ion_charge(path):
    '''Reads recursively every directory under path and
    outputs HTML/JSON for each data.ion file'''
    config_check()
    config_load()
    for dirpath, subdirs, filenames in os.walk(path):
        #removing '.' of the path in the case of root directory of site
        dirpath = re.sub('^\.$|\.\/', '', dirpath)
        if not has_data_file(dirpath):
            continue
        page_data = get_page_data(dirpath)
        # get timestamp and convert to date format set in config
        page_data['date'] = date_format(page_data['date'], \
            CFG['date_format'])
        save_json(dirpath, page_data)
        save_html(dirpath, page_data)
    # after generating all pages, update feed
    save_rss()


def ion_spark(path):
    '''Creates a new page in specified path'''
    config_check()
    config_load()
    if not os.path.exists(path):
        os.makedirs(path)
    data_file = os.path.join(path, CFG['data_file'])
    if os.path.exists(data_file):
        sys.exit('Zap! Page \'{0}\' already exists \
with a data.ion file.'.format(path))
    else:
        # saving timestamp
        date = time.mktime(datetime.now().timetuple())
        # copy source file to new path
        with open(data_file, 'w') as f:
            f.write(DATA_MODEL.format(date))
        # saves data to file listing all pages created
        update_index(path)
        print('Page \'{0}\' successfully created.'.format(path))
        print('Edit the file {0} and call\
\'ion charge\'!'.format(data_file))


def ion_plug():
    '''Installs Ion on the current folder'''
    system_path, config_path = system_pathinfo()
    print('Installing Ion...')
    # Creates system folder
    if not os.path.exists(system_path):
        print('System folder:\t{0}'.format(system_path))
        os.makedirs(system_path)
    if not os.path.exists(config_path):
        # Creates config file from CFG_MODEL
        print('Config file:\t{0}'.format(config_path))
        with open(config_path, 'w') as f:
            f.write(CFG_MODEL)
    # load the config after creating the system folder
    config_load()
    # Creating themes directory
    if not os.path.exists(CFG['themes_path']):
        os.makedirs(CFG['themes_path'])
    dft_themepath = os.path.join(CFG['themes_path'], CFG['default_theme'])
    dft_tplpath = os.path.join(dft_themepath, CFG['template_file'])
    # Creating default theme directory
    if not os.path.exists(dft_themepath):
        print('Default theme:\t{0}'.format(dft_themepath))
        os.makedirs(dft_themepath)
    # Creating default template file
    if not os.path.exists(dft_tplpath):
        print('Default template file:\t{0}'.format(dft_tplpath))
        with open(dft_tplpath, 'w') as f:
            f.write(TEMPLATE_MODEL)
    # Index log file with list of recent pages
    if not os.path.exists(CFG['index_path']):
        print('Index file:\t{0}'.format(CFG['index_path']))
        with open(CFG['index_path'], 'w') as f:
            f.close()
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
