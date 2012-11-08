# coding: utf-8

import re
import os
import sys

import quark

RE_START = '\{\{\s*'
RE_END = '\s*\}\}'
CMD_LIST = 'print|pagelist|include'

class TagParser:
    def __init__(self, variables, index):
        self.variables = variables
        self.index = index

    def print(self, key):
        return self.variables.get(key, '')
    
    def pagelist(self, num, category = None, tpl_file = None):
        if not self.index:
            return ''
        index = self.index[:]
        if num != '*':
            try:
                num = int(num)
            except ValueError:
                return ''
            # listing order
            if num > 0:
                index.reverse()
            index = index[:num]
        if category:
            f = lambda c: c.startswith(os.path.join(category, ''))
            index = filter(f, index)
        pagelist = ''
        for page in index:
            page_data = quark.get_page_data(page)
            permalink = page_data['permalink']
            title = page_data['title']
            pagelist += '<a href="{0}">{1}</a>\n'.format(permalink, title)
        return pagelist
    
    def include(self, tpl_file):
        pass


def parse(variables, tpl, index=None):
    '''Replaces the page variables in the given template'''
    regex = RE_START + '(' + CMD_LIST + ')' + '\s+(.*?)' + RE_END
    tags_matched = re.findall(re.compile(regex), tpl)
    # variables format: [('print', 'x'), ('pagelist', '4 blog')]
    tag_parser = TagParser(variables, index)
    for tag in tags_matched:
        cmd, args = tag
        value = getattr(tag_parser, cmd)(*args.split())
        tag_re = re.compile(RE_START + cmd + '\s+' + args + RE_END)
        tpl = re.sub(tag_re, value, tpl)
    return tpl
