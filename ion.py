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

# templating language
import photon
# IO module, basic bricks
import quark

# obey the rules
if sys.version_info.major < 3:
    sys.exit('Zap! Ion requires Python 3!')


def system_pathinfo():
    system_path = os.path.join(os.getcwd(), quark.CFG['system_dir'])
    config_path = os.path.join(system_path, quark.CFG['config_file'])
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


def config_load():
    '''Loads the config file in system folder'''
    system_path, config_path = system_pathinfo()
    for key, value in quark.parse_ion_file(config_path).items():
        quark.CFG[key] = value
    # add a trailing slash to base url, if necessary
    quark.CFG['base_url'] = os.path.join(quark.CFG['base_url'], '')
    system_url = os.path.join(quark.CFG['base_url'], quark.CFG['system_dir'])
    quark.CFG['themes_url'] = os.path.join(system_url, quark.CFG['themes_dir'], '')
    quark.CFG['themes_path'] = os.path.join(system_path, quark.CFG['themes_dir'])
    quark.CFG['index_path'] = os.path.join(system_path, quark.CFG['index_file'])


def date_format(timestamp, fmt):
    '''helper to convert a timestamp into a given date format'''
    timestamp = float(timestamp)
    return datetime.fromtimestamp(timestamp).strftime(fmt)


def update_index(path):
    '''Updates a log file containing list of all pages created'''
    if path == '.':
        return
    pageline = '{0}\n'.format(path)
    with open(quark.CFG['index_path'], 'a') as f:
        f.write(pageline)


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
    theme_dir = os.path.join(quark.CFG['themes_path'], page_data['theme'])
    tpl_filepath = os.path.join(theme_dir, quark.CFG['template_file'])
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
    # loading recent pages index
    index = quark.get_page_index()
    html = photon.parse(page_data, html_tpl, index)
    with open(os.path.join(path, 'index.html'), 'w') as f:
        f.write(html)
    print('\'{0}\' generated.'.format(path))


def save_rss():
    rss_data = {}
    # loading recent pages index
    index = quark.get_page_index()
    if not len(index):
        return
    rss_data['site_name'] = quark.CFG['site_name']
    rss_data['link'] = quark.CFG['base_url']
    rss_data['description'] = quark.CFG['site_description']
    items = []
    # will get only the first n items
    max_items = int(quark.CFG['rss_items'])
    for page in index[:max_items]:
        page = page.strip()  # remove newlines
        if not quark.has_data_file(page):
            continue
        page_data = quark.get_page_data(page)
        # get timestamp and convert to rfc822 date format
        rfc822_fmt = '%a, %d %b %Y %H:%M:%S ' + quark.CFG['utc_offset']
        page_data['date'] = date_format(page_data['date'], rfc822_fmt)
        # get last page date to fill lastBuildDate
        rss_data['build_date'] = page_data['date']
        items.append(photon.parse(page_data, quark.RSS_ITEM_MODEL))
    items.reverse()  # the last inserted must be the first in rss
    rss_data['items'] = '\n'.join(items)
    rss = photon.parse(rss_data, quark.RSS_MODEL)
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
        if not quark.has_data_file(dirpath):
            continue
        page_data = quark.get_page_data(dirpath)
        # get timestamp and convert to date format set in config
        page_data['date'] = date_format(page_data['date'], \
            quark.CFG['date_format'])
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
    data_file = os.path.join(path, quark.CFG['data_file'])
    if os.path.exists(data_file):
        sys.exit('Zap! Page \'{0}\' already exists \
with a data.ion file.'.format(path))
    else:
        # saving timestamp
        date = time.mktime(datetime.now().timetuple())
        # copy source file to new path
        with open(data_file, 'w') as f:
            f.write(quark.DATA_MODEL.format(date))
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
        # Creates config file from quark.CFG_MODEL
        print('Config file:\t{0}'.format(config_path))
        with open(config_path, 'w') as f:
            f.write(quark.CFG_MODEL)
    # load the config after creating the system folder
    config_load()
    # Creating themes directory
    if not os.path.exists(quark.CFG['themes_path']):
        os.makedirs(quark.CFG['themes_path'])
    dft_themepath = os.path.join(quark.CFG['themes_path'], quark.CFG['default_theme'])
    dft_tplpath = os.path.join(dft_themepath, quark.CFG['template_file'])
    # Creating default theme directory
    if not os.path.exists(dft_themepath):
        print('Default theme:\t{0}'.format(dft_themepath))
        os.makedirs(dft_themepath)
    # Creating default template file
    if not os.path.exists(dft_tplpath):
        print('Default template file:\t{0}'.format(dft_tplpath))
        with open(dft_tplpath, 'w') as f:
            f.write(quark.TEMPLATE_MODEL)
    # Index log file with list of recent pages
    if not os.path.exists(quark.CFG['index_path']):
        print('Index file:\t{0}'.format(quark.CFG['index_path']))
        with open(quark.CFG['index_path'], 'w') as f:
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
