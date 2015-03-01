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

from datetime import datetime

REQUIRED_KEYS = ('title', 'date')


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
    
    def __len__(self):
        return 0

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
        for key in params.keys():
            method_name = 'set_{}'.format(key)
            if hasattr(self, method_name):
                getattr(self, method_name)(params[key], options)
            else:
                self.data[key] = params[key]
        for key in REQUIRED_KEYS:
            if key in params:
                continue
            msg = 'The following value was not defined: {!r}'
            raise ValuesNotDefinedError(msg.format(key))
    
    def add_child(self, page):
        '''Link books in a familiar way'''
        self.children.insert(page)

    def set_template(self, tpl, options):
        '''To give a book a good look and diagramation'''
        self.template = tpl

    def set_date(self, date_string, options):
        '''converts date string to datetime object'''
        try:
            date_format = options.get('date_format', '')
            date = datetime.strptime(date_string, date_format)
            self['date'] = date
            self['year'] = date.year
            self['month'] = date.month
            self['day'] = date.day
        except ValueError:
            raise PageValueError('Wrong date format '
            'detected at {!r}!'.format(self.path))

    def convert_param_list(self, param):
        '''Convert param string to list'''
        if isinstance(param, str):
            return [x.strip() for x in param.split(',')]
        return param

    def set_props(self, props, options):
        '''Books can have some different properties'''
        self.props = self.convert_param_list(props)

    def set_styles(self, styles, options):
        '''To get some extra style'''
        self.styles = self.convert_param_list(styles)

    def set_scripts(self, scripts, options):
        '''To get some extra behavior'''
        self.scripts = self.convert_param_list(scripts)

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
        self.pages = []

    def __iter__(self):
        for page in self.pages:
            yield page

    def __len__(self):
        return len(self.pages)
    
    def __setitem__(self, key, value):
        self.pages[key] = value

    def __getitem__(self, key):
        return self.pages[key]
    
    def __delitem__(self, key):
        del self.pages[key]
    
    def reverse(self):
        '''To reverse the list of books'''
        return self.pages.reverse()

    def page_struct(self, index):
        '''To create a tag to find books'''
        page = self.pages[index]
        return {
            'url': page['url'],
            'title': page['title']
        }

    def paginate(self):
        '''To sort books in shelves'''
        length = len(self.pages)
        for index, page in enumerate(self.pages):
            page['first'] = self.page_struct(0)
            next_index = index + 1 if index < length - 1 else -1
            page['next'] = self.page_struct(next_index)
            prev_index = index - 1 if index > 0 else 0
            page['prev'] = self.page_struct(prev_index)
            page['last'] = self.page_struct(-1)

    def insert(self, page):
        '''To insert book in right position by date'''
        count = 0
        while True:
            if count == len(self.pages) or page <= self.pages[count]:
                self.pages.insert(count, page)
                break
            count += 1