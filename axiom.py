# coding: utf-8

'''
===============================================================================
Mnemonix - The Static Publishing System of Nimus Ages

Author: Karlisson M. Bezerra
E-mail: contact@hacktoon.com
URL: https://github.com/hacktoon/mnemonix
License: WTFPL - http://sam.zoy.org/wtfpl/COPYING

===============================================================================
'''

import os
import json
import re
import shutil
from datetime import datetime

import book_dweller

from mem import MemReader
from page import Page, PageList
from stamper.stamper import Stamper
from alarum import (ValuesNotDefinedError, FileNotFoundError,
                        SiteAlreadyInstalledError, PageExistsError,
                        PageValueError, TemplateError)


BASE_URL = 'http://localhost/'
TEMPLATES_DIR = 'templates'
DATA_DIR = 'data'
DATA_FILE = 'page.me'
CONFIG_FILE = 'config.me'
FEED_FILE = 'feed.xml'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
DEFAULT_TEMPLATE = 'default'
FEED_DIR = 'feed'
FEED_NUM = 8
TEMPLATES_EXT = '.tpl'
JSON_FILENAME = 'data.json'
HTML_FILENAME = 'index.html'

MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(MODEL_DIR, DATA_DIR)
BASE_PATH = os.curdir


class Category:
    '''Define a category of pages'''
    def __init__(self, name):
        self.name = name
        self.pages = PageList()

    def add_page(self, page):
        '''To add a book to a category'''
        self.pages.insert(page)
    
    def paginate(self):
        '''To sort books in the shelves'''
        self.pages.paginate()


class CategoryList:
    '''Define a list of categories'''
    def __init__(self):
        self.items = {}

    def __iter__(self):
        for category in self.items.values():
            yield category

    def add_category(self, category_name):
        '''To create a new category of books'''
        if category_name in self.items.keys() or not category_name:
            return
        self.items[category_name] = Category(category_name)

    def add_page(self, category_name, page):
        '''To add a book to a specific category in a list'''
        if not category_name:
            return
        if category_name not in self.items.keys():
            self.add_category(category_name)
        self.items[category_name].add_page(page)


class Renderer:
    def __init__(self, template, tpl_name):
        self.template = template
        self.tpl_name = tpl_name
        self.include_path = ''

    def render(self, context):
        cache = context['render_cache']
        if self.tpl_name in cache.keys():
            renderer = cache[self.tpl_name]
        else:
            renderer = Stamper(self.template, 
                filename=self.tpl_name, include_path=self.include_path)
            cache[self.tpl_name] = renderer
        return renderer.render(context)


class JSONRenderer(Renderer):
    def __init__(self):
        pass

    def render(self, page):
        page_data = page.data.copy()
        page_data['date'] = page['date'].strftime(DATE_FORMAT)
        return json.dumps(page_data, skipkeys=True)


class HTMLRenderer(Renderer):
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
        '''Show a book in HTML format'''
        self.include_path = env.get('templates_dir', TEMPLATES_DIR)
        page_data = page.data.copy()
        page_data['styles'] = self.build_style_tags(page.styles)
        page_data['scripts'] = self.build_script_tags(page.scripts)
        env['page'] = page_data
        return super().render(env)


class MechaniScribe:
    '''An infinite automaton that can write books at a blazing speed'''
    def __init__(self, meta=None):
        self.page_list = PageList()
        self.categories = CategoryList()
        self.meta = meta or {}

    def read_page(self, path):
        '''Return the page data specified by path'''
        data_file_path = self.meta.get('data_file', DATA_FILE)
        file_path = os.path.join(path, data_file_path)
        if os.path.exists(file_path):
            file_content = book_dweller.bring_file(file_path)
            try:
                mem_data = MemReader(file_content).parse()
            except PageValueError as err:
                raise PageValueError('In file {!r}: {}'.format(file_path, err))
            return mem_data
        return

    def build_page(self, path, page_data):
        '''Page object factory'''
        options = {}
        page = Page()
        page.path = re.sub(r'^\.$|\./|\.\\', '', path)
        options['date_format'] = self.meta.get('date_format', DATE_FORMAT)
        base_url = self.meta.get('base_url', BASE_URL)
        page_data['url'] = book_dweller.urljoin(base_url, page.path) + '/'
        if 'category' in page_data.keys():
            cat_name = page_data.get('category', '')
            category_url = book_dweller.urljoin(base_url, cat_name) + '/'
        else:
            category_url = base_url + '/'
        page_data['category_url'] = category_url
        content = page_data.get('content', '')
        regexp = r'<!--\s*more\s*-->'
        page_data['excerpt'] = re.split(regexp, content, 1)[0]
        page_data['content'] = re.sub(regexp, '', content)
        try:
            page.initialize(page_data, options)
        except ValuesNotDefinedError as error:
            raise ValuesNotDefinedError('{} at page {!r}'.format(error, path))
        if not page.template:
            page.template = self.meta.get('default_template', 
            DEFAULT_TEMPLATE)
        return page
    
    def read_page_tree(self, path, parent=None):
        '''Read the folders recursively and create an ordered list
        of page objects.'''
        if os.path.basename(path) in self.meta.get('blocked_dirs'):
            return
        page_data = self.read_page(path)
        page = None
        if page_data:
            page = self.build_page(path, page_data)
            page.parent = parent
            if page.is_listable():
                self.categories.add_page(page['category'], page)
            if parent:
                parent.add_child(page)
            # add page to ordered list of pages
            if not page.is_draft():
                self.page_list.insert(page)
        for subpage_path in self.read_subpages_list(path):
            self.read_page_tree(subpage_path, page)

    def read_subpages_list(self, path):
        '''Return a list containing the full path of the subpages'''
        for folder in os.listdir(path):
            fullpath = os.path.join(path, folder)
            if os.path.isdir(fullpath):
                yield fullpath

    def read_template(self, tpl_filename):
        '''To return a template string from the template folder'''
        templates_dir = self.meta.get('templates_dir', TEMPLATES_DIR )
        tpl_filepath = os.path.join(templates_dir, tpl_filename)
        tpl_filepath += TEMPLATES_EXT
        if not os.path.exists(tpl_filepath):
            raise FileNotFoundError('Template {!r}'
            ' not found'.format(tpl_filepath))
        return book_dweller.bring_file(tpl_filepath)
    
    def write_json(self, page):
        '''To write the book data in a style-free, raw format'''
        if 'nojson' in page.props:
            return
        json_path = os.path.join(page.path, self.meta.get('json_filename',
            JSON_FILENAME))
        output = JSONRenderer().render(page)
        book_dweller.write_file(json_path, output)

    def write_html(self, page, env):
        '''To write a book in the HTML format'''
        if 'nohtml' in page.props:
            return
        template = self.read_template(page.template)
        renderer = HTMLRenderer(template, page.template)
        html_path = os.path.join(page.path, self.meta.get('html_filename', 
            HTML_FILENAME))
        try:
            output = renderer.render(page, env)
        except TemplateError as error:
            raise TemplateError('{} at template {!r}'.format(error, 
            page.template))
        book_dweller.write_file(html_path, output)
    
    def write_feed(self, env, page_list, name):
        '''To write an announcement about new books'''
        if not len(page_list):
            return
        tpl_filepath = os.path.join(DATA_DIR, FEED_FILE)
        template = book_dweller.bring_file(tpl_filepath)
        feed_dir = self.meta.get('feed_dir', FEED_DIR)
        feed_path = os.path.join(BASE_PATH, feed_dir)
        base_url = self.meta.get('base_url', BASE_URL)
        renderer = Renderer(template, 'rss')
        try:
            feed_num = int(self.meta.get('feed_num', FEED_NUM))
        except ValueError:
            feed_num = FEED_NUM
        if not os.path.exists(feed_path):
            os.makedirs(feed_path)
        
        fname = '{}.xml'.format(name)
        env['feed'] = {
            'link': book_dweller.urljoin(base_url, feed_dir, fname),
            'build_date': datetime.today()
        }
        page_list =  [p for p in page_list if p.is_feed_enabled()]
        page_list.reverse()
        page_list = page_list[:feed_num]
        env['pages'] = page_list
        output = renderer.render(env)
        rss_file = os.path.join(feed_path, fname)
        book_dweller.write_file(rss_file, output)
        return rss_file

    def publish_page(self, page, env):
        '''To actually finishing a book and sending it to the shelves'''
        try:
            self.write_html(page, env)
            self.write_json(page)
        except FileNotFoundError as error:
            raise FileNotFoundError('{} at page {!r}'.format(error, page.path))

    def publish_feeds(self):
        '''To write the announcements of new books to the public'''
        env = { 'site': self.meta, 'render_cache': {}}
        # unique feed
        file_path = self.write_feed(env, self.page_list, 'rss')
        print("Generated {!r}.".format(file_path))
        # generate feeds based on categories
        for cat in self.categories:
            file_path = self.write_feed(env, cat.pages, cat.name)
            if file_path:
                print("Generated {!r}.".format(file_path))
            else:
                print("Category {!r} has no content!".format(cat.name))


class Library:
    '''The Abissal library of wonders'''
    def __init__(self):
        self.meta = {}

    def lookup_config(self, path):
        '''Search a config file upwards in path provided'''
        while True:
            path, _ = os.path.split(path)
            config_path = os.path.join(path, CONFIG_FILE)
            if os.path.exists(config_path):
                return config_path
            if not path:
                break
        return ''

    def build(self, path):
        '''Build the wonder library'''
        config_file = os.path.join(path, CONFIG_FILE)
        templates_dir = os.path.join(path, TEMPLATES_DIR)
        if os.path.exists(config_file):
            raise SiteAlreadyInstalledError('A wonderful library '
            'is already built here!')
        if not os.path.exists(templates_dir):
            model_templates_dir = os.path.join(DATA_DIR, templates_dir)
            shutil.copytree(model_templates_dir, templates_dir)
        if not os.path.exists(config_file):
            model_config_file = os.path.join(DATA_DIR, config_file)
            shutil.copyfile(model_config_file, config_file)

    def enter(self, path):
        '''Load the config'''
        config_path = self.lookup_config(path)
        if not os.path.exists(config_path):
            raise FileNotFoundError
        config_file = book_dweller.bring_file(config_path)
        try:
            self.meta = MemReader(config_file).parse()
        except PageValueError as err:
            raise PageValueError('In file {!r}: {}'.format(config_path, err))
        blocked = self.meta.get('blocked_dirs', [])

    def write_page(self, path):
        '''Create a book in the library'''
        data_file_path = self.meta.get('data_file', DATA_FILE)
        page_file = os.path.join(path, data_file_path)
        if os.path.exists(page_file):
            raise PageExistsError('Page {!r} already exists.'.format(path))
        if not os.path.exists(path):
            os.makedirs(path)
        data_file_path = self.meta.get('data_file', DATA_FILE)
        model_page_file = os.path.join(DATA_DIR, data_file_path)
        content = book_dweller.bring_file(model_page_file)
        date_format = self.meta.get('date_format', DATE_FORMAT)
        date = datetime.today().strftime(date_format)
        book_dweller.write_file(page_file, content.format(date))

    def publish_pages(self, path):
        '''Send the books to the wonderful Mechaniscriber for rendering'''
        scriber = MechaniScribe(self.meta)
        scriber.read_page_tree(path)
        for cat in scriber.categories:
            cat.paginate()
        pages = scriber.page_list
        env = {
            'pages': [p for p in pages if p.is_listable()],
            'site': self.meta,
            'render_cache': {}
        }
        summary = {'pages': []}
        for page in pages:
            env['page'] = page
            if page.is_json_writable():
                summary['pages'].append(page.path)
            scriber.publish_page(page, env)
            print('Generated page {!r}.'.format(page.path))
        scriber.publish_feeds()

        print('Generated pages summary: {!r}.'.format('pages.json'))
        book_dweller.write_file('pages.json', json.dumps(summary))
        return pages
