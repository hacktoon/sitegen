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


tag_exprs = (
    r'\{\{\s*(list)\s+'
        r'([-a-z0-9_]+)(?:\s+(\d+|\*)(?:\s+([-a-z0-9/_]+|\*))?)?'
        r'\s*\}\}(.+?)\{\{\s*end\s*\}\}',
    r'\{\{\s*(include)\s+([-a-z0-9]+)\s*\}\}',
    r'\{\{\s*(breadcrumbs)\s*\}\}(.+?)\{\{\s*end\s*\}\}',
    r'\{\{\s*([-a-z0-9_]+)\s*\}\}'
)


def tag_list(page_data, src, num, category, tpl):
    '''Prints a list of objects within a given template'''
    # get the list of page data
    page_index = quark.get_page_index()
    # limit the category first
    if category and category != '*':
        bycat_func = lambda c: c.startswith(os.path.join(category, ''))
        page_index = list(filter(bycat_func, page_index))
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
    if page_index:
        for page in page_index:
            item_data = quark.get_page_data(page)
            page_list.append(render_template(tpl, item_data))
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
    path = page_data['path']
    breadcrumbs = []
    while path:
        item_data = quark.get_page_data(path)
        breadcrumbs.insert(0, render_template(tpl, item_data))
        path, page = os.path.split(path)
    return '\n'.join(breadcrumbs)


def render_template(tpl, page_data, tpl_name=None):
    '''Replaces the page variables in the given template'''
    for expr in tag_exprs:
        for match in re.finditer(expr, tpl, re.DOTALL):
            tag_string, tag_data = match.group(0), match.groups()
            cmd_name = "tag_" + tag_data[0]
            if cmd_name in globals():
                tag_value = globals()[cmd_name](page_data, *tag_data[1:])
            elif tag_data[0] in page_data:
                tag_value = page_data[tag_data[0]]
            else:
                sys.exit('Zap! Tag "{}" '
                'could not be parsed!'.format(cmd_name))
            tpl = tpl.replace(tag_string, tag_value)
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