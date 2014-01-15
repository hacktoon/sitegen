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

import specs
import book_dweller

from templex import TemplateParser
from alarum import (ValuesNotDefinedError, FileNotFoundError,
						SiteAlreadyInstalledError, PageExistsError,
						PageValueError, TemplateError)

# aliases
path_join = os.path.join
isdir = os.path.isdir
basename = os.path.basename
listdir = os.listdir


class Category:
	def __init__(self, name):
		self.name = name
		self.pages = PageList()

	def add_page(self, page):
		self.pages.insert(page)
	
	def paginate(self):
		self.pages.paginate()


class PageList:
	def __init__(self):
		self.pages = []

	def __iter__(self):
		for page in self.pages:
			yield page

	def __len__(self):
		return len(self.pages)

	def __getitem__(self, key):
		return self.pages[key]
	
	def reverse(self):
		return self.pages.reverse()

	def page_struct(self, index):
		page = self.pages[index]
		return {
			'url': page['url'],
			'title': page['title']
		}

	def paginate(self):
		length = len(self.pages)
		for index, page in enumerate(self.pages):
			page['first'] = self.page_struct(0)
			next_index = index + 1 if index < length - 1 else -1
			page['next'] = self.page_struct(next_index)
			prev_index = index - 1 if index > 0 else 0
			page['prev'] = self.page_struct(prev_index)
			page['last'] = self.page_struct(-1)

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

	def add_category(self, category_name):
		if category_name in self.items.keys() or not category_name:
			return
		self.items[category_name] = Category(category_name)

	def add_page(self, category_name, page):
		if not category_name:
			return
		if category_name not in self.items.keys():
			self.add_category(category_name)
		self.items[category_name].add_page(page)


class JSONRenderer():
	def render(self, page):
		page_data = page.data.copy()
		page_data['date'] = page['date'].strftime(specs.DATE_FORMAT)
		return json.dumps(page_data, skipkeys=True)


class RSSRenderer():
	def __init__(self, template):
		self.template = template

	def render(self, context):
		renderer = TemplateParser(self.template)
		return renderer.render(context)


class HTMLRenderer():
	def __init__(self, template):
		self.link_tpl = '<link rel="stylesheet" type="text/css" href="{0}"/>'
		self.script_tpl = '<script src="{0}"></script>'
		self.template = template

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
		page_data = page.data.copy()
		page_data['styles'] = self.build_style_tags(page.styles)
		page_data['scripts'] = self.build_script_tags(page.scripts)
		env['page'] = page_data
		renderer = TemplateParser(self.template)
		renderer.set_include_path(env.get('templates_dir', specs.TEMPLATES_DIR))
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
		self.data = {}

	def __le__(self, other):
		return self['date'] <= other['date']

	def __str__(self):
		return 'Page {!r}'.format(self.path)

	def __setitem__(self, key, value):
		self.data[key] = value

	def __getitem__(self, key):
		if not key in self.data.keys():
			return None
		return self.data[key]
	
	def __contains__(self, key):
		return key in self.data.keys()

	def initialize(self, params):
		''' Set properties dynamically '''
		required_keys_cache = list(self.required_keys)
		for key in params.keys():
			method_name = 'set_{}'.format(key)
			if hasattr(self, method_name):
				getattr(self, method_name)(params[key])
			else:
				self.data[key] = params[key]
			if key in required_keys_cache:
				required_keys_cache.remove(key)
		if len(required_keys_cache):
			raise ValuesNotDefinedError('The following values were not defined: {!r}'
			.format(', '.join(required_keys_cache)))
		del self.required_keys
	
	def add_child(self, page):
		self.children.insert(page)

	def set_template(self, tpl):
		self.template = tpl

	def set_props(self, props):
		self.props = book_dweller.extract_multivalues(props)

	def set_styles(self, styles):
		self.styles = book_dweller.extract_multivalues(styles)

	def set_scripts(self, scripts):
		self.scripts = book_dweller.extract_multivalues(scripts)

	def set_date(self, date):
		'''converts date string to datetime object'''
		try:
			self['date'] = datetime.strptime(date, self.date_format)
		except ValueError:
			raise PageValueError('Wrong date format '
			'detected at {!r}!'.format(self.path))

	def is_draft(self):
		return 'draft' in self.props
	
	def is_listable(self):
		return 'nolist' not in self.props and not self.is_draft()

	def is_feed_enabled(self):
		return 'nofeed' not in self.props


class MechaniScribe:
	def __init__(self, meta=None):
		self.page_list = PageList()
		self.categories = CategoryList()
		self.meta = meta or {}
	
	def parse_input_file(self, file_string):
		file_data = {}
		lines = file_string.split('\n')
		for num, line in enumerate(lines):
			# avoids empty lines and comments
			line = line.strip()
			if not line or line.startswith('#'):
				continue
			if(line == 'content'):
				# read the rest of the file
				file_data['content'] = ''.join(lines[num + 1:])
				break
			key, value = [l.strip() for l in line.split('=', 1)]
			file_data[key] = value
		return file_data

	def read_page(self, path):
		'''Return the page data specified by path'''
		file_path = path_join(path, self.meta.get('data_file', specs.DATA_FILE))
		if os.path.exists(file_path):
			return self.parse_input_file(book_dweller.bring_file(file_path))
		return

	def build_page(self, path, page_data):
		'''Page object factory'''
		page = Page()
		page.path = re.sub(r'^\.$|\./|\.\\', '', path)
		page.date_format = self.meta.get('date_format', specs.DATE_FORMAT)
		base_url = self.meta.get('base_url', specs.BASE_URL)
		page_data['url'] = book_dweller.urljoin(base_url, page.path)
		content = page_data.get('content', '')
		regexp = r'<!--\s*more\s*-->'
		page_data['excerpt'] = re.split(regexp, content, 1)[0]
		page_data['content'] = re.sub(regexp, '', content)
		try:
			page.initialize(page_data)
		except ValuesNotDefinedError as e:
			raise ValuesNotDefinedError('{} at page {!r}'.format(e, path))
		if not page.template:
			page.template = self.meta.get('default_template', specs.DEFAULT_TEMPLATE)
		return page
	
	def read_page_tree(self, path, parent=None):
		'''Read the folders recursively and create an ordered list
		of page objects.'''
		if basename(path) in self.meta.get('blocked_dirs'):
			return
		page_data = self.read_page(path)
		page = None
		if page_data:
			page = self.build_page(path, page_data)
			page.parent = parent
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
		for folder in listdir(path):
			fullpath = path_join(path, folder)
			if isdir(fullpath):
				yield fullpath

	def read_template(self, tpl_filename):
		'''Returns a template string from the template folder'''
		templates_dir = self.meta.get('templates_dir', specs.TEMPLATES_DIR )
		tpl_filepath = os.path.join(templates_dir, tpl_filename)
		tpl_filepath += specs.TEMPLATES_EXT
		if not os.path.exists(tpl_filepath):
			raise FileNotFoundError('Template {!r} not found'.format(tpl_filepath))
		return book_dweller.bring_file(tpl_filepath)
	
	def write_json(self, page):
		if 'nojson' in page.props:
			return
		json_path = path_join(page.path, self.meta.get('json_filename',
			specs.JSON_FILENAME))
		output = JSONRenderer().render(page)
		book_dweller.write_file(json_path, output)

	def write_html(self, page, env):
		if 'nohtml' in page.props:
			return
		template = self.read_template(page.template)
		renderer = HTMLRenderer(template)
		html_path = path_join(page.path, self.meta.get('html_filename', 
			specs.HTML_FILENAME))
		try:
			output = renderer.render(page, env)
		except TemplateError as e:
			raise TemplateError('{} at template {!r}'.format(e, 
			page.template))
		book_dweller.write_file(html_path, output)

	def publish_page(self, page, env):
		if 'draft' in page.props:
			return
		try:
			self.write_html(page, env)
			self.write_json(page)
		except FileNotFoundError as e:
			raise FileNotFoundError('{} at page {!r}'.format(e, page.path))

	def publish_feeds(self):
		tpl_filepath = os.path.join(specs.DATA_DIR, specs.FEED_FILE)
		template = book_dweller.bring_file(tpl_filepath)
		renderer = RSSRenderer(template)
		feed_dir = self.meta.get('feed_dir', specs.FEED_DIR)
		try:
			feed_num = int(self.meta.get('feed_num', specs.FEED_NUM))
		except ValueError:
			feed_num = specs.FEED_NUM
		feed_path = path_join(specs.BASE_PATH, feed_dir)
		if not os.path.exists(feed_path):
			os.makedirs(feed_path)
		env = { 'site': self.meta }
		base_url = self.meta.get('base_url', specs.BASE_URL)
		# generate feeds based on categories
		for cat in self.categories:
			fname = '{}.xml'.format(cat.name)
			env['feed'] = {
				'link': book_dweller.urljoin(base_url, feed_dir, fname),
				'build_date': datetime.today()
			}
			page_list =  [p for p in cat.pages if p.is_feed_enabled()]
			page_list.reverse()
			env['pages'] = page_list[:feed_num]
			output = renderer.render(env)
			rss_file = path_join(feed_path, fname)
			book_dweller.write_file(rss_file, output)
			print("Generated {!r}.".format(rss_file))


class Library:
	def __init__(self):
		self.meta = {}

	def build(self, path):
		'''Build the wonder library'''
		config_file = path_join(path, specs.CONFIG_FILE)
		templates_dir = path_join(path, specs.TEMPLATES_DIR)
		if os.path.exists(config_file):
			raise SiteAlreadyInstalledError("A wonderful library is already built here!")
		if not os.path.exists(templates_dir):
			model_templates_dir = path_join(specs.DATA_DIR, templates_dir)
			shutil.copytree(model_templates_dir, templates_dir)
		if not os.path.exists(config_file):
			model_config_file = path_join(specs.DATA_DIR, config_file)
			shutil.copyfile(model_config_file, config_file)
	
	def lookup_config(self, path):
		'''Search a config file upwards in path provided'''
		while True:
			path, dirname = os.path.split(path)
			config_path = path_join(path, specs.CONFIG_FILE)
			if os.path.exists(config_path):
				return config_path
			if not path:
				break
		return ''

	def enter(self, path):
		'''Load the config'''
		config_path = self.lookup_config(path)
		if not os.path.exists(config_path):
			raise FileNotFoundError()
		scriber = MechaniScribe()
		config_file = book_dweller.bring_file(config_path)
		self.meta = scriber.parse_input_file(config_file)
		blocked_dirs = self.meta.get('blocked_dirs', [])
		self.meta['blocked_dirs'] = book_dweller.extract_multivalues(blocked_dirs)

	def write_page(self, path):
		page_file = path_join(path, self.meta.get('data_file', specs.DATA_FILE))
		if os.path.exists(page_file):
			raise PageExistsError('Page {!r} already exists.'.format(path))
		if not os.path.exists(path):
			os.makedirs(path)
		model_page_file = path_join(specs.DATA_DIR, self.meta.get('data_file', specs.DATA_FILE))
		content = book_dweller.bring_file(model_page_file)
		date_format = self.meta.get('date_format', specs.DATE_FORMAT)
		date = datetime.today().strftime(date_format)
		book_dweller.write_file(page_file, content.format(date))

	def publish_pages(self, path):
		scriber = MechaniScribe(self.meta)
		scriber.read_page_tree(path)
		for cat in scriber.categories:
			cat.paginate()
		pages = scriber.page_list
		env = {
			'pages': pages,
			'site': self.meta
		}
		for page in pages:
			env['page'] = page
			scriber.publish_page(page, env)
			print("Generated page {!r}.".format(page.path))
		scriber.publish_feeds()
