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
        theme_dir = quark.get_current_theme_dir(self.variables['theme'])
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
    return ''.join(tag_list)


def build_style_tags(filenames, permalink):
    tag = '<link rel="stylesheet" type="text/css" href="{0}" />\n'
    return build_external_tags(filenames, permalink, tag, '.css')


def build_script_tags(filenames, permalink):
    tag = '<script src="{0}"></script>\n'
    return build_external_tags(filenames, permalink, tag, '.js')


def save_json(dirname, page_data):
    json_filepath = os.path.join(dirname, 'index.json')
    quark.write_file(json_filepath, json.dumps(page_data))


def save_html(path, page_data):
    theme_dir = quark.get_current_theme_dir(page_data['theme'])
    tpl_filepath = os.path.join(theme_dir, quark.CFG['template_file'])
    if not os.path.exists(tpl_filepath):
        sys.exit('Zap! Template file {0} couldn\'t be \
found!'.format(tpl_filepath))
    #abrindo arquivo de template e extraindo o html
    html_tpl = quark.read_file(tpl_filepath)
    # get css and javascript found in the folder
    css = page_data.get('css', '')
    page_data['css'] = build_style_tags(css, page_data['permalink'])
    js = page_data.get('js', '')
    page_data['js'] = build_script_tags(js, page_data['permalink'])
    # fill template with page data
    # loading recent pages index
    index = quark.get_page_index()
    html = parse(page_data, html_tpl, index)
    quark.write_file(os.path.join(path, 'index.html'), html)
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
        page_data['date'] = quark.date_format(page_data['date'], rfc822_fmt)
        # get last page date to fill lastBuildDate
        rss_data['build_date'] = page_data['date']
        items.append(parse(page_data, quark.RSS_ITEM_MODEL))
    items.reverse()  # the last inserted must be the first in rss
    rss_data['items'] = '\n'.join(items)
    rss = parse(rss_data, quark.RSS_MODEL)
    quark.write_file('rss.xml', rss)


