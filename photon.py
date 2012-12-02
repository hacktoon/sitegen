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


def tag_print(page_data, key):
    '''Prints a variable value, returns nothing if inexistent'''
    return page_data.get(key, '')


def tag_pagelist(page_data, num, category='*', tpl='pagelist-item'):
    '''Prints a list of recent pages'''
    # pagelist *|x|-x [*|cat_name [tpl_name]]
    # loading recent pages index
    page_index = quark.get_page_index()
    # limit the category first
    if category and category != '*':
        tmp_func = lambda c: c.startswith(os.path.join(category, ''))
        page_index = list(filter(tmp_func, page_index))
        #print(page_index, abs(num), page_index[:abs(num)])
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
    pagelist = ''
    for page in page_index:
        item_data = quark.get_page_data(page)
        list_tpl = quark.read_html_template(page_data['theme'], tpl)
        pagelist += render_template(list_tpl, item_data)
    return pagelist


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

'''def tag_breadcrumb(page_data):
    path = page_data['path'].strip('/')
    crumbs = []
    for page in path.split('/'):
        page_crumb = quark.get_page_data(page)
        crumbs.append(page_crumb['permalink'])
    return '/'.join(crumbs)
'''

def render_template(tpl, page_data):
    '''Replaces the page variables in the given template'''
    re_start = '\{\{\s*'
    re_end = '\s*\}\}'
    # this will match with {{cmd arg1 arg2 ...}}
    regex = re_start + '(.*?)' + '\s+(.*?)' + re_end
    # returns: [('print', 'x'), ('pagelist', '4 blog')]
    tags_matched = re.findall(re.compile(regex), tpl)
    # tag command list mapped to functions
    commands = {
        'print': tag_print,
        'pagelist': tag_pagelist,
        'include': tag_include
    }
    for tag in tags_matched:
        cmd_name, args = tag
        value = '' # if the tag isn't in the hash, replace by nothing
        if cmd_name in commands:
            # calls a function and passes a expanded parameter list
            try:
                value = commands[cmd_name](page_data, *args.split())
            except TypeError:
                sys.exit('Zap! The template tag "{0}" \
is incorrect with args "{1}"!'.format(cmd_name, args))
        # replaces the given value in the tag
        regex = re_start + cmd_name + '\s+' + re.escape(args) + re_end
        tag_re = re.compile(r'{0}'.format(regex))
        tpl = re.sub(tag_re, value, tpl)
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