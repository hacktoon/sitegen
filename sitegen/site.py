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
from datetime import datetime

from . import reader
from . import utils
from .template import HTMLTemplate, Template
from .paging import PageList, PageBuilder
from .categorization import CategoryList
from .exceptions import (PageValueError, TemplateError)


BASE_URL = '//localhost/'
STATIC_DIR = 'static'
TEMPLATES_DIR = 'templates'
TEMPLATES_EXT = 'tpl'
DATA_FILE = 'page.me'
IMAGE_FILE = 'image.png'

FEED_FILE = 'feed.xml'
FEED_DIR = 'feed'
FEED_NUM = 8
HTML_FILENAME = 'index.html'
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(MODEL_DIR, '../data')
FORBIDDEN_DIRS = set((STATIC_DIR, TEMPLATES_DIR, FEED_DIR))


class SiteGenerator:
    def __init__(self, props=None):
        self.pagelist = PageList()
        self.category_list = CategoryList()
        self.props = props or {}
        self.base_path = self.props.get('base_path', '')
        self.page_builder = PageBuilder(self.props)

    def read_page(self, path):
        '''Return the page data specified by path'''
        data_file_path = self.props.get('data_file', DATA_FILE)
        file_path = os.path.join(path, data_file_path)
        if not os.path.exists(file_path):
            return

        try:
            page_data = reader.parse(utils.read_file(file_path))
        except PageValueError as err:
            raise PageValueError('In file {!r}: {}'.format(file_path, err))
        page_data['path'] = path

        image_file_name = self.props.get('image_file', IMAGE_FILE)
        image_path = os.path.join(path, image_file_name)
        if os.path.exists(image_path):
            page_data['image'] = image_file_name
        return page_data

    def build_categories(self):
        category_entry = self.props.get('categories', {})
        render_list = []
        base_url = self.props['base_url']
        for key in category_entry.keys():
            item = category_entry[key]
            category = self.category_list.add_category(key)
            url = item.get('url', key)
            category['url'] = utils.urljoin(base_url, url)
            category['title'] = item.get('title', '')
            category['template'] = item.get('template')
            render_list.append({
                'id': category['id'],
                'title': category['title'],
                'url': category['url']
            })
        return render_list

    def build_page(self, page_data, parent_page):
        page = self.page_builder.build(page_data, parent_page)

        category_id = page_data.get('category')
        category = self.category_list[category_id]

        if category_id in self.props.get('categories', {}).keys():
            page['category'] = category.get_dict()
            if page.is_listable():
                category.add_page(page)
        page.category = category

        if not page.template:
            if category and category['template']:
                page.template = category['template']
            else:
                # TODO: warn if default_template is empty
                # make it the object rule to require a default_template
                page.template = self.props.get('default_template')
        return page

    def read_page_tree(self, path, parent_page=None):
        if path in self.props.get('blocked_dirs'):
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

    def read_subpages_list(self, path):
        for filename in os.listdir(path or os.curdir):
            fullpath = os.path.join(path, filename)
            if not os.path.isdir(fullpath):
                continue
            basedir = os.path.dirname(fullpath)
            basename = os.path.basename(fullpath)
            if set((basedir, basename)).intersection(FORBIDDEN_DIRS):
                continue
            yield fullpath

    def write_html(self, page, env):
        if 'nohtml' in page.props:
            return
        templates_dir = self.props.get('templates_dir', TEMPLATES_DIR)
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
        html_filename = self.props.get('html_filename', HTML_FILENAME)
        html_path = os.path.join(page.path, html_filename)
        utils.write_file(html_path, output)

    def publish_page(self, page, env):
        try:
            self.write_html(page, env)
        except FileNotFoundError as error:
            raise FileNotFoundError('{} at page {!r}'.format(error, page.path))

    def publish_feeds(self):
        env = { 'site': self.props, 'template_cache': {}}
        file_path = self.write_feed(env, self.pagelist, 'rss')
        print("Generated RSS {!r}.".format(file_path))

    def write_feed(self, env, pagelist, name):
        if not len(pagelist):
            return
        template = Template(FEED_FILE, os.path.join(DATA_DIR, FEED_FILE))
        try:
            feed_num = int(self.props.get('feed_num', FEED_NUM))
        except ValueError:
            feed_num = FEED_NUM

        dirname = self.props.get('feed_dir', FEED_DIR)
        basepath = os.path.join(self.base_path, dirname)
        if not os.path.exists(basepath):
            os.makedirs(basepath)

        pagelist = [p for p in pagelist if p.is_feed_enabled()]
        pagelist.reverse()
        base_url = self.props['base_url']
        filename = '{}.xml'.format(name)
        env['pages'] = pagelist[:feed_num]
        env['feed'] = {
            'link': utils.urljoin(base_url, dirname, filename),
            'build_date': datetime.today()
        }
        rss_file = os.path.join(basepath, filename)
        utils.write_file(rss_file, template.render(env))
        return rss_file


class Site:
    def __init__(self, props):
        self.props = props

    def generate(self, path):
        self.props['base_path'] = path.rstrip(os.path.sep)
        self.props['base_url'] = os.environ.get('URL', BASE_URL)

        generator = SiteGenerator(self.props)
        category_list = generator.build_categories()

        generator.read_page_tree(path)
        for cat in generator.category_list:
            cat.paginate()
        pages = generator.pagelist
        env = {
            'pages': [p for p in pages if p.is_listable()],
            'site': self.props,
            'categories': category_list,
            'template_cache': {}
        }

        for page in pages:
            env['page'] = page
            generator.publish_page(page, env)
            print('Generated HTML {!r}.'.format(page.path))
        generator.publish_feeds()
        return pages
