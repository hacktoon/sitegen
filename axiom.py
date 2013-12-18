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
import sys
import re
import shutil
from datetime import datetime

import mechaniscribe

from templex import TemplateParser
from alarum import (ValuesNotDefinedError, FileNotFoundError,
						SiteAlreadyInstalledError, PageExistsError,
						PageValueError, TemplateError)


class Category:
	def __init__(self, name):
		self.name = name
		self.pages = PageList()
		self.pages.pagination = True

	def add_page(self, page):
		self.pages.insert(page)


class PageList:
	def __init__(self):
		self.pages = []
		self.pagination = False

	def __iter__(self):
		for page in self.pages:
			yield page

	def __len__(self):
		return len(self.pages)

	def __getitem__(self, key):
		return self.pages[key]

	def paginate(self):
		if not self.pagination:
			return
		length = len(self.pages)
		for index, page in enumerate(self.pages):
			page.first = self.pages[0]
			next_index = index + 1 if index < length - 1 else -1
			page.next = self.pages[next_index]
			prev_index = index - 1 if index > 0 else 0
			page.prev = self.pages[prev_index]
			page.last = self.pages[-1]

	def insert(self, page):
		'''Insert page in list ordered by date'''
		count = 0
		while True:
			if count == len(self.pages) or page <= self.pages[count]:
				self.pages.insert(count, page)
				break
			count += 1


class CategoryList:
	def __init__(self):
		self.items = {}

	def __iter__(self):
		for category in self.items.values():
			yield category

	def add_category(self, name):
		if name in self.items.keys() or not name:
			return
		self.items[category_name] = Category(category_name)

	def add_page(self, category_name, page):
		if category_name not in self.items.keys() or not category_name:
			return
		self.items[category_name].add_page(page)


class ContentRenderer():
	def __init__(self, template):
		self.template = self.read_template(template)

	def read_template(self, tpl_filename):
		'''Returns a template string from the template folder'''
		tpl_filepath = os.path.join(TEMPLATES_DIR, tpl_filename)
		tpl_filepath += TEMPLATES_EXT
		if not os.path.exists(tpl_filepath):
			raise FileNotFoundError('Template {!r} not found'.format(tpl_filepath))
		return utils.read_file(tpl_filepath)

	def render(self):
		pass


class JSONRenderer(ContentRenderer):
	def __init__(self):
		pass

	def render(self, page):
		page = vars(page)
		return json.dumps(page, skipkeys=True)


class RSSRenderer(ContentRenderer):
	def render(self, context):
		renderer = TemplateParser(self.template)
		return renderer.render(context)


class HTMLRenderer(ContentRenderer):
	def __init__(self, template):
		super().__init__(template)
		self.link_tpl = '<link rel="stylesheet" type="text/css" href="{0}"/>'
		self.script_tpl = '<script src="{0}"></script>'

	def build_external_tags(self, links, tpl):
		tag_list = []
		for link in links:
			tag_list.append(tpl.format(link))
		return '\n'.join(tag_list)

	def build_style_tags(self, links):
		if not links:
			return ''
		links = [f for f in links if f.endswith('.css')]
		return self.build_external_tags(links, self.link_tpl)

	def build_script_tags(self, links):
		if not links:
			return ''
		links = [f for f in links if f.endswith('.js')]
		return self.build_external_tags(links, self.script_tpl)

	def render(self, page, env):
		page.styles = self.build_style_tags(page.styles)
		page.scripts = self.build_script_tags(page.scripts)
		env['page'] = page
		renderer = TemplateParser(self.template)
		renderer.set_include_path(TEMPLATES_DIR)
		return renderer.render(env)



class Page():
	def __init__(self):
		self.required_keys = ('title', 'date')
		self.children = PageList()
		self.parent = None
		self.props = []
		self.styles = []
		self.scripts = []
		self.template = ''
		self.category = ''
		self.data = {}

	def __le__(self, other):
		return self['date'] <= other['date']

	def __str__(self):
		return 'Page {!r}'.format(self.path)

	def __getitem__(self, key):
		if not key in self.data.keys():
			return None
		return self.data[key]
	
	def initialize(self, params):
		''' Set properties dynamically '''
		required_keys_cache = list(self.required_keys)
		for key in params.keys():
			method_name = 'set_{}'.format(key)
			if hasattr(self, method_name):
				getattr(self, method_name)(params[key])
			else:
				self[key] = params[key]
			if key in required_keys_cache:
				required_keys_cache.remove(key)
		if len(required_keys_cache):
			raise ValuesNotDefinedError('The following values were not defined: {!r}'
			.format(', '.join(required_keys_cache)))
		del self.required_keys
	
	def add_child(self, page):
		self.children.insert(page)

	def set_props(self, props):
		self.props = utils.extract_multivalues(props)

	def set_styles(self, styles):
		self.styles = utils.extract_multivalues(styles)

	def set_scripts(self, scripts):
		self.scripts = utils.extract_multivalues(scripts)

	def set_date(self, date):
		'''converts date string to datetime object'''
		try:
			self.date = datetime.strptime(date, DATE_FORMAT)
		except ValueError:
			raise PageValueError('Wrong date format '
			'detected at {!r}!'.format(self.path))

	def is_listable(self):
		return 'nolist' not in self.props

	def is_feed_enabled(self):
		return 'nofeed' not in self.props

	def generate_json(self):
		if 'nojson' in self.props:
			return
		output = JSONRenderer().render(self)
		utils.write_file(os.path.join(self.path, JSON_FILENAME), output)

	def generate_html(self, env):
		if 'nohtml' in self.props:
			return
		renderer = HTMLRenderer(self.template)
		output = renderer.render(self, env)
		utils.write_file(os.path.join(self.path, HTML_FILENAME), output)

	def render(self, env):
		if 'draft' in self.props:
			return
		self.generate_json()
		env['page'] = self
		try:
			self.generate_html(env)
		except TemplateError as e:
			raise TemplateError('{} at template {!r}'.format(e, 
			self.template))
		except FileNotFoundError as e:
			raise FileNotFoundError('{} at page {!r}'.format(e, self.path))


class Library:
	def __init__(self):
		self.categories = CategoryList()
		self.pages = PageList()
		self.meta = {}
	
	def build(self, path, base_specs):
		cwd = os.path.dirname(os.path.abspath(__file__))
		data_dir = os.path.join(cwd, base_specs['data_dir'])
		config_file = os.path.join(path, base_specs['config_file'])
		templates_dir = os.path.join(path, base_specs['templates_dir'])
		
		if os.path.exists(config_file):
			raise SiteAlreadyInstalledError("A wonderful library is already built here!")
		
		if not os.path.exists(templates_dir):
			model_templates_dir = os.path.join(data_dir, templates_dir)
			shutil.copytree(model_templates_dir, templates_dir)

		if not os.path.exists(config_file):
			model_config_file = os.path.join(data_dir, config_file)
			shutil.copyfile(model_config_file, config_file)
	
	def get_metadata(self, path):
		if not os.path.exists(path):
			raise FileNotFoundError("No library found in this place!")
		return self.meta
	
	def set_metadata(self, config):
		self.meta = utils.parse_input_file(utils.read_file(self.path))

	def set_base_url(self, base_url):
		if not base_url:
			base_url = 'http://localhost'
		self.base_url = base_url.strip('/')

	def set_feed_dir(self, feed_dir):
		self.feed_dir = feed_dir or 'feed'

	def set_feed_num(self, feed_num):
		try:
			self.feed_num = int(feed_num)
		except ValueError:
			self.feed_num = 8

	def set_default_template(self, template):
		self.default_template = template
