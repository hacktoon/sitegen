# coding: utf-8

'''
==============================================================================
Ion - A shocking simple static (site) generator

Author: Karlisson M. Bezerra
E-mail: contact@hacktoon.com
URL: https://github.com/karlisson/ion
License: WTFPL - http://sam.zoy.org/wtfpl/COPYING

==============================================================================
'''

import re
import os
import sys
import json

import quark


def tag_print(tags, page_data, tpl, tpl_name):
    '''Returns a variable value and instructions to replace'''
    # example tag: ('print', ['variable'], (7, 19))
    tag = tags[0] # takes the first print command
    key = tag[1][0] # takes the variable name
    return (page_data.get(key, ''), tag[2], 1)


def tag_pagelist(tags, page_data, tpl, tpl_name):
    '''Prints a list of objects within a given template'''
    # example tag: ('pagelist', ['variable'], (7, 19))
    args = tags[1]
    num = category = None
    args = args.split()
    arg_length = len(args)
    if arg_length == 2:
        num, category = args
    elif arg_length == 1:
        num = args[0]
    # get the list of page data
    page_index = quark.get_page_index()
    # limit the category first
    if category and category != '*':
        tmp_func = lambda c: c.startswith(os.path.join(category, ''))
        data_list = list(filter(tmp_func, page_index))
    # limit number of pages to show
    if num != '*':
        try:
            num = int(num)
        except ValueError:
            sys.exit('Zap! Bad argument "{0}" at template tag!'.format(num))
        # listing order
        if num > 0:
            page_index.reverse()
        page_index = page_index[:abs(num)]
    page_list = []
    # replace page. prefix from variable names
    tpl = tpl.replace('page.', '')
    if page_index:
        for page in page_index:
            item_data = quark.get_page_data(page)
            page_list.append(render_template(tpl, item_data))
    else:
        return render_template(tpl_empty, page_data)
    return '\n'.join(page_list)


def tag_include(page_data, filename):
    theme_dir = quark.get_page_theme_dir(page_data['theme'])
    if not filename.endswith('.tpl'):
        filename = '{0}.tpl'.format(filename)
    path = os.path.join(theme_dir, filename)
    if os.path.exists(path):
        include_tpl = quark.read_file(path)
        return render_template(include_tpl, page_data)
    else:
        print('Warning: Include file \'{0}\' doesn\'t exists.'.format(path))
        return ''


def tag_breadcrumbs(page_data, tpl):
    levels = os.path.split(page_data['path'])
    breadcrumbs = ''
    for page in levels:
        render_template(tpl, page_data)
    
    return breadcrumbs


def parse_tags(tpl):
    # returns [('print', ['variavel'], (7, 19)), 
    # ('pagelist', ['4', 'blog'], (20, 39))]
    tag_start = tag_end = 0
    cmd_end = cmd_start = 0
    in_tag = False
    tags = []
    for m in re.finditer(r'\{\{|\}\}', tpl):
        match = m.group(0)
        if match == '{{' and in_tag:
            sys.exit('error')
        if match == '}}' and not in_tag:
            sys.exit('error')
        if match == '{{':
            in_tag = True
            tag_start = m.start()
            cmd_start = m.end()
        else:
            in_tag = False
            cmd_end = m.start()
            tag_end = m.end()
            cmd = tpl[cmd_start:cmd_end].strip()
            tag_string = re.split(r'\s+', cmd)
            cmd, args = tag_string[0], tag_string[1:]
            tags.append((cmd, args, (tag_start, tag_end)))
    return tags


def render_template(tpl, page_data, tpl_name=None):
    '''Replaces the page variables in the given template'''
    replacements = []
    tags = parse_tags(tpl)
    idx = 0
    while idx < len(tags):
        tag = tags[idx]
        # sample return data in get_tags:
        # cmd, args & position of tag in tpl string
        # sample data: [('print', ['variavel'], (7, 19)),
        # ('pagelist', ['4', 'blog'], (20, 39))]
        cmd_name = 'tag_'+tag[0]
        if not cmd_name in globals():
            sys.exit('Zap! Command "{0}" does not exists!'.format(cmd_name))
        replaces = globals()[cmd_name](tags[idx:], page_data, tpl, tpl_name)
        replacements.append(replaces)
        idx += replace_info

    return tpl


def build_external_tags(filenames, permalink, tpl):
    tag_list = []
    for filename in filenames:
        filename = filename.strip()
        url = os.path.join(permalink, filename)
        tag_list.append(tpl.format(url))
    return '\n'.join(tag_list)


def build_style_tags(filenames, permalink):
    tpl = '<link rel="stylesheet" type="text/css" href="{0}"/>'
    filenames = [f for f in filenames.split(',') if f.endswith('css')]
    return build_external_tags(filenames, permalink, tpl)


def build_script_tags(filenames, permalink):
    tpl = '<script src="{0}"></script>'
    filenames = [f for f in filenames.split(',') if f.endswith('js')]
    return build_external_tags(filenames, permalink, tpl)


def save_json(dirname, page_data):
    json_filepath = os.path.join(dirname, 'index.json')
    quark.write_file(json_filepath, json.dumps(page_data))


def save_html(path, page_data):
    html_tpl = quark.read_html_template(page_data['theme'], \
        page_data['template'])
    # get css and javascript found in the folder
    permalink = page_data['permalink']
    page_data['css'] = build_style_tags(page_data.get('css', ''), permalink)
    page_data['js'] = build_script_tags(page_data.get('js', ''), permalink)
    # replace template with page data and listings
    html = render_template(html_tpl, page_data)
    quark.write_file(os.path.join(path, 'index.html'), html)
    # remove ./ and . from path names
    path = re.sub(r'\./|\.', '', path)
    if path:
        print('Page "{0}" generated.'.format(path))
    else:
        print('Root page generated.')


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
    max_items = int(site_config.get('rss_items', 0))
    # get the templates: full rss document and rss item snippets
    rss_tpl, rss_item_tpl = quark.read_rss_templates()
    # populate RSS items with the page index
    for page in index[:max_items]:
        page_data = quark.get_page_data(page)
        pdate, ptime = quark.get_datetime(page_data)
        page_data['date'] = quark.date_to_rfc822(pdate, ptime)
        # get last page date to fill lastBuildDate
        rdate, rtime = quark.get_datetime()
        rss_data['build_date'] = quark.date_to_rfc822(rdate, rtime)
        items.append(render_template(rss_item_tpl, page_data))
    items.reverse()  # the last inserted must be the first in rss
    rss_data['items'] = '\n'.join(items)
    rss_doc = render_template(rss_tpl, rss_data)
    quark.write_file('rss.xml', rss_doc)
    print('Feed "rss.xml" generated.')