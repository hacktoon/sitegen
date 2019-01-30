# coding: utf-8

'''
===============================================================================
Infiniscribe - The Infinite Automaton Scriber of Nimus Ages

Author: Karlisson M. Bezerra
E-mail: contact@hacktoon.com
URL: https://github.com/hacktoon/infiniscribe
License: WTFPL - http://sam.zoy.org/wtfpl/COPYING
===============================================================================
'''

import os
import re
import bisect
from datetime import datetime
from . import utils

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
THUMB_FILENAME = 'thumb.png'
THUMB_FILENAME = 'thumb.png'
EXCERPT_RE = r'<!--\s*more\s*-->'


class Page():
    '''Define a page'''
    def __init__(self):
        self.children = PageList()
        self.props = []
        self.path = ''
        self.styles = []
        self.scripts = []
        self.template = ''
        self.data = {}

    def __le__(self, other):
        return self['date'] <= other['date']

    def __lt__(self, other):
        return self['date'] < other['date']

    def __len__(self):
        return 0

    def __bool__(self):
        return True

    def __str__(self):
        return 'Page {!r}'.format(self.path)

    def __setitem__(self, key, value):
        self.data[key] = value

    def __getitem__(self, key):
        return self.data.get(key)

    def __delitem__(self, key):
        del self.data[key]

    def __contains__(self, key):
        return key in self.data.keys()

    def initialize(self, params, options):
        ''' Set books properties dynamically'''
        if 'title' not in params.keys():
            msg = 'The title was not provided!'
            raise ValueError(msg.format(key))

        for key in params.keys():
            method_name = 'set_{}'.format(key)
            if hasattr(self, method_name):
                getattr(self, method_name)(params[key], options)
            else:
                self.data[key] = params[key]

    def add_child(self, page):
        '''Link books in a familiar way'''
        self.children.insert(page)

    def set_date(self, date, _):
        self['date'] = date
        self['year'] = date.year
        self['month'] = date.month
        self['day'] = date.day

    def set_template(self, tpl, options):
        '''To give a book a good look and diagramation'''
        self.template = tpl

    def convert_param_list(self, param):
        '''Convert param string to list'''
        if isinstance(param, str):
            return [x.strip() for x in param.split(',')]
        return param

    def set_props(self, props, options):
        '''Books can have some different properties'''
        self.props = self.convert_param_list(props)

    def set_styles(self, styles, opts):
        '''To get some extra style'''
        styles = self.convert_param_list(styles)
        self.styles = ["{}/{}".format(opts['page_url'], s) for s in styles]

    def set_scripts(self, scripts, opts):
        '''To get some extra behavior'''
        scripts = self.convert_param_list(scripts)
        self.scripts = ["{}/{}".format(opts['page_url'], s) for s in scripts]

    def is_draft(self):
        '''To decide if the book is not ready yet'''
        return 'draft' in self.props

    def is_listable(self):
        '''Sometimes a book shall not be listed'''
        return 'nolist' not in self.props and not self.is_draft()

    def is_feed_enabled(self):
        '''Sometimes book publishers are shy'''
        return 'nofeed' not in self.props

    def is_json_enabled(self):
        '''Sometimes book publishers like other formats'''
        return 'nojson' not in self.props


class PageList:
    '''Define an ordered list of pages'''
    def __init__(self):
        self.ordered_pages = []
        self.page_dict = {}

    def __iter__(self):
        for page in self.ordered_pages:
            yield page

    def __len__(self):
        return len(self.ordered_pages)

    def __setitem__(self, key, value):
        self.ordered_pages[key] = value

    def __getitem__(self, key):
        return self.ordered_pages[key]

    def __delitem__(self, key):
        del self.ordered_pages[key]

    def reverse(self):
        '''To reverse the list of books'''
        return self.ordered_pages.reverse()

    def page_struct(self, index):
        '''To create a tag to find books'''
        page = self.ordered_pages[index]
        return {
            'url': page['url'],
            'title': page['title']
        }

    def paginate(self):
        '''To sort books in shelves'''
        length = len(self.ordered_pages)
        for index, page in enumerate(self.ordered_pages):
            page['first'] = self.page_struct(0)
            next_index = index + 1 if index < length - 1 else -1
            page['next'] = self.page_struct(next_index)
            prev_index = index - 1 if index > 0 else 0
            page['prev'] = self.page_struct(prev_index)
            page['last'] = self.page_struct(-1)

    def insert(self, page):
        '''To insert book in right position by date'''
        bisect.insort(self.ordered_pages, page)
        self.page_dict[page.path] = page


class PageBuilder:
    def __init__(self, env):
        self.env = env

    def build_url_from_path(self, path):
        resource = path.replace(self.env['base_path'], '').strip('/')
        return utils.urljoin(self.env['base_url'], resource)

    def build_thumbnail(self, page_url):
        thumb_filepath = os.path.join(page_url, THUMB_FILENAME)
        if os.path.exists(thumb_filepath):
            return thumb_filepath
        # TODO: return default thumbnail

    def build_date(self, date_string, date_format):
        '''converts date string to datetime object'''
        if not date_string:
            return datetime.now()
        try:
            date = datetime.strptime(date_string, date_format)
        except ValueError:
            raise PageValueError('Wrong date format '
            'in {!r}!'.format(self.path))
        return date

    def build_content(self, page_data):
        content = page_data.get('content', '')
        page_data['excerpt'] = re.split(EXCERPT_RE, content, 1)[0]
        page_data['content'] = re.sub(EXCERPT_RE, '', content)

    def build_breadcrumbs(self, parent_page, page_data):
        links = []
        template = '<li><a href="{}">{}</a></li>'
        current_page = template.format(page_data['url'], page_data['title'])
        links.insert(0, current_page)
        while parent_page:
            breadcrumb = template.format(parent_page['url'], parent_page['title'])
            links.insert(0, breadcrumb)
            parent_page = parent_page.parent
        # remove all but home page url
        return ''.join(links[1:])

    def build(self, page_data, parent_page):
        '''Page object factory'''
        options = {}
        page = Page()

        page.parent = parent_page
        page.path = page_data['path']

        page_url = self.build_url_from_path(page.path)
        options['date_format'] = self.env.get('date_format', DATE_FORMAT)
        options['page_url'] = page_url

        page_data['url'] = page_url
        page_data['thumb'] = self.build_thumbnail(page_url)
        page_data['breadcrumbs'] = self.build_breadcrumbs(parent_page, page_data)

        page_data['date'] = self.build_date(page_data.get('date'), options.get('date_format', ''))

        self.build_content(page_data)

        try:
            page.initialize(page_data, options)
        except ValueError as error:
            raise ValueError('{} at page {!r}'.format(error, page.path))


        return page
