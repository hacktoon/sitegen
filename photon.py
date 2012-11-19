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

import re
import os
import sys
import json
from datetime import datetime

import quark

RE_START = '\{\{\s*'
RE_END = '\s*\}\}'
CMD_LIST = 'print|pagelist|include'

class TagParser:
    def __init__(self, variables, index):
        self.variables = variables
        self.index = index


    def print(self, key):
        '''Prints a variable value'''
        return self.variables.get(key, '')


    def pagelist(self, num, category = None, preset = 'default'):
        '''Prints a list of recent pages'''
        if not self.index:
            return ''
        index = self.index[:]
        if num != 'all' or num != '*':
            try:
                num = int(num)
            except ValueError:
                return ''
            # listing order
            if num > 0:
                index.reverse()
            index = index[:abs(num)]
        if category:
            tmpf = lambda c: c.startswith(os.path.join(category, ''))
            index = filter(tmpf, index)
        pagelist = ''
        for page in index:
            page_data = quark.get_page_data(page)
            tpl = quark.get_pagelist_preset(page_data['theme'], preset)
            pagelist += tpl.format(**page_data)
        return pagelist


    def include(self, filename):
        theme_dir = quark.get_page_theme_dir(self.variables['theme'])
        path = os.path.join(theme_dir, filename + '.inc')
        if os.path.exists(path):
            return quark.read_file(path)
        else:
            print('Warning: Include file \'{0}\' doesn\'t exists.'.format(path))
            return ''


def parse(variables, tpl, index=None):
    '''Replaces the page variables in the given template'''
    regex = RE_START + '(' + CMD_LIST + ')' + '\s+(.*?)' + RE_END
    tags_matched = re.findall(re.compile(regex), tpl)
    # variables format: [('print', 'x'), ('pagelist', '4 blog')]
    tag_parser = TagParser(variables, index)
    for tag in tags_matched:
        cmd, args = tag
        value = getattr(tag_parser, cmd)(*args.split())
        regex = RE_START + cmd + '\s+' + re.escape(args) + RE_END
        tag_re = re.compile(r'{0}'.format(regex))
        tpl = re.sub(tag_re, value, tpl)
    return tpl


def build_external_tags(filenames, permalink, tag, ext):
    tag_list = []
    for filename in filenames.split(','):
        filename = filename.strip()
        url = os.path.join(permalink, filename)
        if filename.endswith(ext):
            tag_list.append(tag.format(url))
    return '\n'.join(tag_list)


def build_style_tags(filenames, permalink):
    tag = '<link rel="stylesheet" type="text/css" href="{0}" />'
    return build_external_tags(filenames, permalink, tag, 'css')


def build_script_tags(filenames, permalink):
    tag = '<script src="{0}"></script>'
    return build_external_tags(filenames, permalink, tag, 'js')


def save_json(dirname, page_data):
    json_filepath = os.path.join(dirname, 'index.json')
    quark.write_file(json_filepath, json.dumps(page_data))


def save_html(path, page_data):
    html_tpl = quark.read_html_template(page_data['theme'])
    # get css and javascript found in the folder
    permalink = page_data['permalink']
    page_data['css'] = build_style_tags(page_data.get('css', ''), permalink)
    page_data['js'] = build_script_tags(page_data.get('js', ''), permalink)
    # loading recent pages index
    index = quark.get_page_index()
    # replace template with page data and listings
    html = parse(page_data, html_tpl, index)
    quark.write_file(os.path.join(path, 'index.html'), html)
    print('\'{0}\' generated.'.format(path))


def save_rss():
    rss_data = {}
    # loading recent pages index
    index = quark.get_page_index()
    if not len(index):
        return
    site_config = quark.get_site_config()
    rss_data['site_name'] =site_config.get('site_name')
    rss_data['link'] = site_config.get('base_url')
    rss_data['description'] = site_config.get('site_description')
    items = []
    # will get only the first n items
    max_items = int(site_config.get('rss_items'))
    # get the templates: full rss document and rss item snippets
    rss_tpl, rss_item_tpl = quark.read_rss_templates()
    # populate RSS items with the page index
    for page in index[:max_items]:
        page_data = quark.get_page_data(page)
        # get date and convert to rfc822 date format
        rfc822_fmt = '%a, %d %b %Y %H:%M:%S ' + site_config.get('utc_offset')
        date = datetime.strptime(page_data['date'], site_config['date_format'])
        page_data['date'] = date.strftime(rfc822_fmt)
        # get last page date to fill lastBuildDate
        rss_data['build_date'] = page_data['date']
        items.append(parse(page_data, rss_item_tpl))
    items.reverse()  # the last inserted must be the first in rss
    rss_data['items'] = '\n'.join(items)
    rss_doc = parse(rss_data, rss_tpl)
    quark.write_file('rss.xml', rss_doc)