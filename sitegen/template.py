# coding: utf-8

'''
===============================================================================
Sitegen

Author: Karlisson M. Bezerra
E-mail: contact@hacktoon.com
URL: https://github.com/hacktoon/sitegen
License: WTFPL - http://sam.zoy.org/wtfpl/COPYING
===============================================================================
'''

import os
import json
import sys

from . import reader
from . import utils
from .paging import Page, PageList
from .categorization import Category, CategoryList
from .stamper.stamper import Stamper
from .exceptions import TemplateError

# set to env global date format
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
TEMPLATES_DIR = 'templates'
DEFAULT_TEMPLATE = 'default'
TEMPLATES_EXT = 'tpl'


class Template:
    def __init__(self, id, path):
        self.id = id
        if not os.path.exists(path):
            raise FileNotFoundError('Template {!r}'
            ' not found'.format(path))
        self.content = utils.read_file(path)
        self.path = path
        self.include_path = ''

    def render(self, context):
        cache = context['template_cache']
        if self.id in cache.keys():
            tree = cache[self.id]
        else:
            tree = Stamper(self.content, include_path=self.include_path)
            cache[self.id] = tree
            if 'page' in context:
                page_content = context['page'].get('content', '')
                context['page']['content'] = Stamper(page_content).render(context)
        return tree.render(context)


class JSONTemplate(Template):
    def __init__(self):
        pass

    def render(self, page):
        page_data = page.data.copy()
        page_data['date'] = page['date'].strftime(DATE_FORMAT)
        return json.dumps(page_data, skipkeys=True)


class HTMLTemplate(Template):
    '''Manage HTML rendering process'''
    def build_external_tags(self, links, tpl):
        '''To help in organization'''
        tag_list = []
        for link in links:
            tag_list.append(tpl.format(link))
        return '\n'.join(tag_list)

    def build_style_tags(self, links):
        '''To organize the book style'''
        if not links:
            return ''
        link_tpl = '<link rel="stylesheet" type="text/css" href="{0}"/>'
        links = [f for f in links if f.endswith('.css')]
        return self.build_external_tags(links, link_tpl)

    def build_script_tags(self, links):
        '''To organize the behavior scripts'''
        if not links:
            return ''
        script_tpl = '<script src="{0}"></script>'
        links = [f for f in links if f.endswith('.js')]
        return self.build_external_tags(links, script_tpl)

    def render(self, page, env):
        page_data = page.data.copy()
        page_data.update({
            'styles': self.build_style_tags(page.styles),
            'scripts': self.build_script_tags(page.scripts)
        })
        env['page'] = page_data
        return super().render(env)
