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

# default template with all basic template variables
TEMPLATE_MODEL = '''<!DOCTYPE html>
<html>
<head>
    <meta name="author" content="{{print site_author}}" />
    <meta name="description" content="{{print site_description}}" />
    <meta name="keywords" content="{{print tags}}" />
    <meta charset="UTF-8" />
    <link rel="stylesheet" href="{{print themes_url}}bolt/ion.css" type="text/css" />
    {{print css}}
    <title>{{print title}} | {{print site_name}}</title>
</head>
<body>
    <h1><a href="{{print base_url}}">{{print site_name}}</a></h1>
    <p>{{print site_description}}</p>
    <ul>
        <li><a href="{{print base_url}}">Home</a></li>
        <li><a href="{{print base_url}}about">About</a></li>
        {{pagelist 3}}
    </ul>
    <h2><a href="{{print permalink}}">{{print title}}</a></h2>
    <span>{{print date}}</span>
    <p>{{print content}}</p>
    <h2>Included menu</h2>
    <p>{{include footer}}</p>
    {{print js}}
</body>
</html>
'''

# model of RSS file for feed generation
RSS_MODEL = '''<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0"
    xmlns:atom="http://www.w3.org/2005/Atom"
>
<channel>
    <title>{{print site_name}}</title>
    <atom:link href="{{print link}}rss.xml" rel="self" type="application/rss+xml" />
    <link>{{print link}}</link>
    <description>{{print description}}</description>
    <lastBuildDate>{{print build_date}}</lastBuildDate>
    {{print items}}
</channel>
</rss>
'''

RSS_ITEM_MODEL = '''
    <item>
        <title>{{print title}}</title>
        <link>{{print permalink}}</link>
        <pubDate>{{print date}}</pubDate>
        <description><![CDATA[{{print content}}]]></description>
        <guid>{{print permalink}}</guid>
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

DEFAULT_PAGELIST_PRESET = '''<li>
    <a title="{title}" href="{permalink}">
        {title}
    </a>
</li>
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
