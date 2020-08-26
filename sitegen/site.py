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
import sys
import re
import shutil
from datetime import datetime

from . import utils

from . import paging
from .paging import Page, PageList

from .filesystem import FileSystem
from .template import HTMLTemplate, Template
from .exceptions import (PageExistsError,
                         PageValueError, TemplateError)


STATIC_DIR = 'static'
TEMPLATES_DIR = 'templates'
TEMPLATES_EXT = 'tpl'
IMAGE_FILE = 'image.png'

FEED_FILE = 'feed.xml'
FEED_DIR = 'feed'
FEED_NUM = 8
HTML_FILENAME = 'index.html'
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(MODEL_DIR, '../data')


class SiteGenerator:
    def __init__(self, config=None):
        self.pagelist = PageList()
        self.config = config or {}
        self.base_path = self.config.get('base_path', '')

    def build_categories(self):
        category_entry = self.config.get('categories', {})
        render_list = []
        base_url = self.config['base_url']
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

    def read_page(self, path):
        '''Return the page data specified by path'''
        try:
            page_data = reader.parse(utils.read_file(file_path))
        except PageValueError as err:
            raise PageValueError('In file {!r}: {}'.format(file_path, err))
        page_data['path'] = path

        image_file_name = self.config.get('image_file', IMAGE_FILE)
        image_path = os.path.join(path, image_file_name)
        if os.path.exists(image_path):
            page_data['image'] = image_file_name
        return page_data

    def write_html(self, page, env):
        if 'nohtml' in page.config:
            return
        templates_dir = self.config.get('templates_dir', TEMPLATES_DIR)
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
        html_filename = self.config.get('html_filename', HTML_FILENAME)
        html_path = os.path.join(page.path, html_filename)
        utils.write_file(html_path, output)

    def publish_page(self, page, env):
        try:
            self.write_html(page, env)
        except FileNotFoundError as error:
            raise FileNotFoundError('{} at page {!r}'.format(error, page.path))

    def publish_feeds(self):
        env = { 'site': self.config, 'template_cache': {}}
        file_path = self.write_feed(env, self.pagelist, 'rss')
        print("Generated RSS {!r}.".format(file_path))

    def write_feed(self, env, pagelist, name):
        if not len(pagelist):
            return
        template = Template(FEED_FILE, os.path.join(DATA_DIR, FEED_FILE))
        try:
            feed_num = int(self.config.get('feed_num', FEED_NUM))
        except ValueError:
            feed_num = FEED_NUM

        dirname = self.config.get('feed_dir', FEED_DIR)
        basepath = os.path.join(self.base_path, dirname)
        if not os.path.exists(basepath):
            os.makedirs(basepath)

        pagelist = [p for p in pagelist if p.is_feed_enabled()]
        pagelist.reverse()
        base_url = self.config['base_url']
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
    def __init__(self, config):
        self.config = config
        self.base_url = os.environ.get('URL', 'http://localhost')

    def generate(self, path):
        data_path = path + '/data'
        build_path = path + '/build'

        filesystem = FileSystem()
        nodes = filesystem.read(data_path)

        # for folder in filesystem:
        #     page = paging.build_page(folder, self.base_url)
        #     print(page)
        # #     env['page'] = page
        # #     generator.publish_page(page, env)
        # return []


        # for cat in generator.category_list:
        #     cat.paginate()
        # pages = generator.pagelist
        # env = {
        #     'pages': [p for p in pages if p.is_listable()],
        #     'site': self.config,
        #     'template_cache': {}
        # }

        # for page in pages:
        #     env['page'] = page
        #     generator.publish_page(page, env)
        #     # print('Generated HTML {!r}.'.format(page.path))
        # generator.publish_feeds()
        return []  # pages
