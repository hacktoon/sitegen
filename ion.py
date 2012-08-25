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

# obey the rules
if sys.version_info.major < 3:
    sys.exit('Zap! Ion requires Python 3!')

# model of RSS file for feed generation
RSS_MODEL = '''
<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
<channel>
    <title></title>
    <link></link>
    <pubDate></pubDate>
    <description></description>
    <item>
        <title></title>
        <link></link>
        <description></description>
    </item>
</channel>
</rss>
'''

# this is the model of files used to store content
# it will be saved to a new file data.ion every
# time 'ion spark' is called
DATA_MODEL = '''title: Write your title here
date: yyyy-mm-dd
content:
Write your content here
'''

# pre-configuration values
CFG = {
    'system_dirname': '_ion',
    'base_url': 'http://localhost/',
    'themes_dirname': 'themes',
    'default_theme': 'ionize',
    'blocked_dirs': [],
    'template_file': 'index.html',
    'cache_file': 'cache.ion',
    'source_file': 'data.ion',
    'config_file': 'config.ion'
}

# initialize some config data
# getcwd allows calling ion.py from wherever it is located in system
# example return: /home/user/site/_ion
CFG['system_path'] = os.path.join(os.getcwd(), CFG['system_dirname'])
# returns the path of the custom config: /home/user/site/_ion/config.ion
CFG['config_path'] = os.path.join(CFG['system_path'], CFG['config_file'])
CFG['themes_path'] = os.path.join(CFG['system_path'], CFG['themes_dirname'])
CFG['cache_path'] = os.path.join(CFG['system_path'], CFG['config_file'])
CFG['themes_url'] = os.path.join(CFG['base_url'], CFG['system_dirname'], CFG['themes_dirname'])

def parse_config_file(file_path):
    '''Parse a configuration file and returns data in a dictionary'''
    config_file = open(file_path).readlines()
    # remove trailing whitespaces and linebreaks
    lines = [line.strip() for line in config_file]
    config = {}
    for line in lines:
        # avoid comments, empty and incorrect lines
        if line.startswith('#') or not len(line) or '=' not in line:
            continue
        key, value = line.split('=')
        config[key.strip()] = value.strip()
    return config

def load_config():
    '''Loads the config file in system folder'''
    if not os.path.exists(CFG['system_path']):
        sys.exit('Zap! System folder "{0}" doesn\'t exists. It must \
be in the same directory that ion.py is called.'.format(CFG['system_path']))
    try:
        config = parse_config_file(CFG['config_path'])
    except:
        sys.exit('Zap! Could not load configuration file!')
    
    # FIXME
    #cache_file = os.path.join(CFG['system_path'], CFG['cache_file'])
    #if not os.path.exists(cache_file):
    #    cache_file = open(cache_file, 'w')
    # try to set a default value if it wasn't defined in config
    # add a trailing slash, if necessary
    CFG['base_url'] = os.path.join(config.get('base_url', CFG['base_url']), '')
    # get default theme, if it is defined in config
    CFG['default_theme'] = config.get('default_theme', CFG['default_theme'])
    # folders you don't want Ion to enter
    # returns the system path by default
    blocked = config.get('blocked_dirs', CFG['system_dirname'])
    for folder in blocked.split(','):
        CFG['blocked_dirs'].append(folder.strip())

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

def get_page_data(source_path):
    '''Parses *.ion data files and returns the values'''
    source_file = open(source_path, 'r')
    page_data = {}
    while True:
        line = source_file.readline()
        # if reached end of file, exit loop
        if len(line) == 0:
            break
        # will avoid splitting blank lines
        try:
            key, value = list(map(str.strip, line.split(':')))
        except:
            continue
        # read the rest of the file
        if(key == 'content'):
            value = value + source_file.read()
        #setting values
        page_data[key] = value
    source_file.close()
    return page_data

def save_json(dirname, page_data):
    json_filepath = os.path.join(dirname, 'index.json')
    json_file = open(json_filepath, 'w')
    json_file.write(json.dumps(page_data))
    json_file.close()

def save_html(dirname, page_data):
    theme_name = CFG['default_theme']
    # if not using custom theme, use default
    if 'theme' in page_data.keys():
        theme_name = page_data['theme']
    theme_dir = os.path.join(CFG['themes_path'], theme_name)
    theme_filepath = os.path.join(theme_dir, CFG['template_file'])
    if not os.path.exists(theme_filepath):
        sys.exit('Zap! Template file {0} couldn\'t be \
found!'.format(theme_filepath))
    #abrindo arquivo de template e extraindo o html
    html = open(theme_filepath, 'r').read()
    # fill template with page data
    html_filepath = os.path.join(dirname, 'index.html')
    html_file = open(html_filepath, 'w')
    for key, value in page_data.items():
        regex = re.compile(r'\{\{\s*' + key + '\s*\}\}')
        html = re.sub(regex, value.strip(), html)
    html_file.write(html)
    html_file.close()
    print('\'{0}\' generated.'.format(html_filepath))

def is_blocked(dirname):
    '''Checks if the actual directory is blocked to generation'''
    return dirname in CFG['blocked_dirs']

def ion_charge(path):
    '''Reads recursively every directory under path and
    outputs HTML/JSON for each data.ion file'''
    for dirpath, subdirs, filenames in os.walk(path):
        #removing '.' of the path in the case of root directory of site
        dirpath = re.sub('^\.$|\.\/', '', dirpath)
        source_filepath = os.path.join(dirpath, CFG['source_file'])
        # tests for blocked directories or
        # directories that doesn't have a source file
        if is_blocked(dirpath) or not os.path.exists(source_filepath):
            continue
        # extracts data from this page
        page_data = get_page_data(source_filepath)
        # set common page data
        page_data['base_url'] = CFG['base_url']
        page_data['themes_url'] = CFG['themes_url']
        permalink = os.path.join(CFG['base_url'], dirpath)
        page_data['permalink'] = permalink
        # get css and javascript found in the folder
        css = page_data.get('css', '')
        page_data['css'] = build_style_tags(css, permalink)
        js = page_data.get('js', '')
        page_data['js'] = build_script_tags(js, permalink)
        # output
        save_json(dirpath, page_data)
        save_html(dirpath, page_data)

def ion_spark(path):
    '''Creates a new page in specified path'''
    if not os.path.exists(path):
        os.makedirs(path)
    filepath = os.path.join(path, CFG['source_file'])
    if os.path.exists(filepath):
        print('Zap! Page \'{0}\' already exists \
with a data.ion file.'.format(path))
    else:
        # copy source file to new path
        data_file = open(filepath, 'w')
        data_file.write(DATA_MODEL)
        data_file.close()
        print('Page \'{0}\' successfully created.'.format(path))
        print('Edit the file {0} and call \'ion charge\'!'.format(filepath))


if __name__ == '__main__':
    help_message = '''Usage:
    ion.py spark [path/to/folder] - Creates a empty page on path specified.
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

    if command == 'spark':
        ion_spark(path)
    elif command == 'charge':
        ion_charge(path)
    elif command == 'help':
        sys.exit(help_message)
    else:
        print('Zap! {0} is a very strange command!'.format(command))
        sys.exit(help_message)
