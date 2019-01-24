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
import json
import re
import shutil
from datetime import datetime

from . import reader
from . import utils
from .template import HTMLTemplate, JSONTemplate, Template
from .paging import Page, PageList, PageBuilder
from .categorization import Category, CategoryList
from .stamper.stamper import Stamper
from .exceptions import (SiteAlreadyInstalledError, PageExistsError,
                         PageValueError, TemplateError)


BASE_URL = 'http://localhost/'
STATIC_DIR = 'static'
TEMPLATES_DIR = 'templates'
DEFAULT_TEMPLATE = 'default'
TEMPLATES_EXT = 'tpl'
DATA_FILE = 'page.me'
CONFIG_FILE = 'config.me'
FEED_FILE = 'feed.xml'
FEED_DIR = 'feed'
FEED_NUM = 8
JSON_FILENAME = 'data.json'
HTML_FILENAME = 'index.html'
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(MODEL_DIR, '../data')
FORBIDDEN_DIRS = set((STATIC_DIR, TEMPLATES_DIR, FEED_DIR))


class MechaniScribe:
    '''An infinite automaton that can write books at a blazing speed'''
    def __init__(self, meta=None):
        self.pagelist = PageList()
        self.category_list = CategoryList()
        self.meta = meta or {}
        self.base_path = self.meta.get('base_path', '')
        self.page_builder = PageBuilder(self.meta)

    def read_page(self, path):
        '''Return the page data specified by path'''
        data_file_path = self.meta.get('data_file', DATA_FILE)
        file_path = os.path.join(path, data_file_path)
        if not os.path.exists(file_path):
            return

        try:
            mem_data = reader.parse(utils.read_file(file_path))
        except PageValueError as err:
            raise PageValueError('In file {!r}: {}'.format(file_path, err))
        mem_data['path'] = path
        return mem_data

    def build_categories(self):
        category_key = 'categories'
        render_list = []
        if category_key not in self.meta:
            return
        category_entry = self.meta[category_key]
        base_url = self.meta['base_url']
        for key in category_entry.keys():
            item = category_entry[key]
            if item.get('blocked'):
                continue
            category = self.category_list.add_category(key)
            url = item.get('url', key)
            category['url'] = utils.urljoin(base_url, url) + '/'
            category['title'] = item.get('title', '')
            category['template'] = item.get('template', DEFAULT_TEMPLATE)
            render_list.append({
                'id': category['id'],
                'title': category['title'],
                'url': category['url']
            })
        return render_list

    def build_page(self, page_data, parent_page):
        page = self.page_builder.build(page_data, parent_page)

        category_id = page_data.get('category', '')
        category = self.category_list[category_id]

        if category and category_id in self.meta.get('categories', {}).keys():
            page['category'] = category.get_dict()
            if page.is_listable():
                category.add_page(page)

        if not page.template:
            if category and category['template']:
                page.template = category['template']
            else:
                page.template = self.meta.get('default_template', DEFAULT_TEMPLATE)

        return page

    def read_page_tree(self, path, parent_page=None):
        '''Read the folders recursively and create an ordered list
        of page objects.'''
        if path in self.meta.get('blocked_dirs'):
            return {}

        page_data = self.read_page(path)
        page = None
        children = {}
        if page_data:
            page = self.build_page(page_data, parent_page)
            # add page to ordered list of pages
            if not page.is_draft():
                self.pagelist.insert(page)
        for sub_page_path in self.read_subpages_list(path):
            child_info = self.read_page_tree(sub_page_path, page or parent_page)
            if child_info:
                children.update(child_info)
        # home page
        if page_data and page_data.get('type') == 'home':
            return children
        # only append this page and its children if
        # it has at least one child or is a page
        is_page = bool(page_data) and page.is_json_enabled() and not page.is_draft()
        if is_page or children:
            path = path.split(os.sep)[-1]
            return {path: 1 if is_page else children}
        return {}

    def read_subpages_list(self, path):
        '''Return a list containing the full path of the subpages'''
        for filename in os.listdir(path or os.curdir):
            fullpath = os.path.join(path, filename)
            if not os.path.isdir(fullpath):
                continue
            basedir = os.path.dirname(fullpath)
            basename = os.path.basename(fullpath)
            if set((basedir, basename)).intersection(FORBIDDEN_DIRS):
                continue
            yield fullpath

    def write_json(self, page):
        '''To write the book data in a style-free, raw format'''
        if 'nojson' in page.props:
            return

        json_path = os.path.join(page.path, self.meta.get('json_filename', JSON_FILENAME))
        output = JSONTemplate().render(page)
        utils.write_file(json_path, output)

    def write_html(self, page, env):
        '''To write a book in the HTML format'''
        if 'nohtml' in page.props:
            return
        templates_dir = self.meta.get('templates_dir', TEMPLATES_DIR)
        templates_dir = os.path.join(self.base_path, templates_dir)
        filename = ".".join([page.template, TEMPLATES_EXT])
        template_path = os.path.join(templates_dir, filename)
        template = HTMLTemplate(page.template, template_path)
        template.include_path = templates_dir

        try:
            output = template.render(page, env)
        except TemplateError as error:
            raise TemplateError('{} at template {!r}'.format(error,
                                template.path))
        html_path = os.path.join(page.path,
                                 self.meta.get('html_filename', HTML_FILENAME))
        utils.write_file(html_path, output)

    def write_feed(self, env, pagelist, name):
        '''To write an announcement about new books'''
        if not len(pagelist):
            return
        template = Template(FEED_FILE, os.path.join(DATA_DIR, FEED_FILE))
        try:
            feed_num = int(self.meta.get('feed_num', FEED_NUM))
        except ValueError:
            feed_num = FEED_NUM

        dirname = self.meta.get('feed_dir', FEED_DIR)
        basepath = os.path.join(self.base_path, dirname)
        if not os.path.exists(basepath):
            os.makedirs(basepath)

        pagelist = [p for p in pagelist if p.is_feed_enabled()]
        pagelist.reverse()
        base_url = self.meta['base_url']
        filename = '{}.xml'.format(name)
        env['pages'] = pagelist[:feed_num]
        env['feed'] = {
            'link': utils.urljoin(base_url, dirname, filename),
            'build_date': datetime.today()
        }
        rss_file = os.path.join(basepath, filename)
        utils.write_file(rss_file, template.render(env))
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
        env = { 'site': self.meta, 'template_cache': {}}
        # unique feed
        file_path = self.write_feed(env, self.pagelist, 'rss')
        print("Generated {!r}.".format(file_path))
        # generate feeds based on categories
        for cat in self.category_list:
            file_path = self.write_feed(env, cat.pagelist, cat['id'])
            if file_path:
                print("Generated {!r}.".format(file_path))
            else:
                print("Category {!r} has no content!".format(cat['id']))


class Library:
    '''The Abissal library of wonders'''
    def __init__(self):
        self.meta = {}

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
        config_path = os.path.join(path, CONFIG_FILE)
        if not os.path.exists(config_path):
            raise FileNotFoundError
        config_file = utils.read_file(config_path)
        try:
            self.meta = reader.parse(config_file)
        except PageValueError as err:
            raise PageValueError('In file {!r}: {}'.format(config_path, err))
        blocked = self.meta.get('blocked_dirs', [])

    def write_page(self, path):
        '''Create a book in the library'''
        scriber = MechaniScribe(self.meta)
        data_file_path = self.meta.get('data_file', DATA_FILE)
        page_file = os.path.join(path, data_file_path)
        if os.path.exists(page_file):
            raise PageExistsError('Page {!r} already exists.'.format(path))
        if not os.path.exists(path):
            os.makedirs(path)
        data_file_path = self.meta.get('data_file', DATA_FILE)
        model_page_file = os.path.join(DATA_DIR, data_file_path)
        content = utils.read_file(model_page_file)
        date_format = self.meta.get('date_format', DATE_FORMAT)
        date = datetime.today().strftime(date_format)
        utils.write_file(page_file, content.format(date))

    def publish_pages(self, path):
        '''Send the books to the wonderful Infiniscriber for rendering'''
        self.meta['base_path'] = path.rstrip(os.path.sep)
        self.meta['base_url'] = self.meta.get('base_url', BASE_URL)

        scriber = MechaniScribe(self.meta)
        category_list = scriber.build_categories()

        json_summary = scriber.read_page_tree(path)
        for cat in scriber.category_list:
            cat.paginate()
        pages = scriber.pagelist
        env = {
            'pages': [p for p in pages if p.is_listable()],
            'site': self.meta,
            'categories': category_list,
            'template_cache': {}
        }

        for page in pages:
            env['page'] = page
            scriber.publish_page(page, env)
            print('Generated page {!r}.'.format(page.path))
        scriber.publish_feeds()

        summary_path = os.path.join(path, 'pages.json')
        utils.write_file(summary_path, json.dumps(json_summary))
        print('Generated file tree summary {!r}'.format(summary_path))

        return pages
