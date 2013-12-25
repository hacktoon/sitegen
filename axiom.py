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
		tpl_filepath = os.path.join(specs.TEMPLATES_DIR, tpl_filename)
		tpl_filepath += specs.TEMPLATES_EXT
		if not os.path.exists(tpl_filepath):
			raise FileNotFoundError('Template {!r} not found'.format(tpl_filepath))
		return book_dweller.bring_file(tpl_filepath)

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
				self.data[key] = params[key]
			if key in required_keys_cache:
				required_keys_cache.remove(key)
		if len(required_keys_cache):
			raise ValuesNotDefinedError('The following values were not defined: {!r}'
			.format(', '.join(required_keys_cache)))
		del self.required_keys
	
	def add_child(self, page):
		self.children.insert(page)

	def set_category(self, cat):
		self.category = cat

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
			self.date = datetime.strptime(date, specs.DATE_FORMAT)
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
		book_dweller.write_file(path_join(self.path, JSON_FILENAME), output)

	def generate_html(self, env):
		if 'nohtml' in self.props:
			return
		renderer = HTMLRenderer(self.template)
		output = renderer.render(self, env)
		book_dweller.write_file(path_join(self.path, HTML_FILENAME), output)

	def render(self, env):
		if 'draft' in self.props:
			return
		#self.generate_json()
		env['page'] = self
		try:
			self.generate_html(env)
		except TemplateError as e:
			raise TemplateError('{} at template {!r}'.format(e, 
			self.template))
		except FileNotFoundError as e:
			raise FileNotFoundError('{} at page {!r}'.format(e, self.path))


class MechaniScribe:
	def __init__(self, meta=None):
		self.page_list = PageList()
		self.meta = meta
	
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
		file_path = path_join(path, specs.DATA_FILE)
		if os.path.exists(file_path):
			return self.parse_input_file(book_dweller.bring_file(file_path))
		return

	def build_page(self, path, page_data):
		'''Page object factory'''
		page = Page()
		page.path = re.sub(r'^\.$|\./|\.\\', '', path)
		page.slug = basename(page.path)
		base_url = self.meta.get('base_url', specs.BASE_URL)
		page.url = book_dweller.urljoin(base_url, page.path)
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
		page_data = self.read_page(path)
		page = None
		if page_data:
			page = self.build_page(path, page_data)
			page.parent = parent
			if parent:
				parent.add_child(page)
			# add page to ordered list of pages
			self.page_list.insert(page)
		for subpage_path in self.read_subpages_list(path):
			self.read_page_tree(subpage_path, page)

	def read_subpages_list(self, path):
		'''Return a list containing the full path of the subpages'''
		for folder in listdir(path):
			fullpath = path_join(path, folder)
			if isdir(fullpath):
				yield fullpath

	def write_feed():
		pass
		
	'''def generate_feeds():
		renderer = RSSRenderer(MODEL_FEED_FILE)
		feed_dir = feed_dir
		if not os.path.exists(feed_dir):
			os.makedirs(feed_dir)
		env = { 'site':  }
		# generate feeds based on categories
		for cat in categories:
			fname = '{}.xml'.format(cat.name)
			env['feed'] = {
				'link': urljoin(base_url, feed_dir, fname),
				'build_date': datetime.today()
			}
			page_list =  [p for p in cat.pages if p.is_feed_enabled()]
			page_list.reverse()
			env['pages'] = page_list[:feed_num]
			output = renderer.render(env)
			rss_file = path_join(feed_dir, fname)
			print("Generated {!r}.".format(rss_file))
			write_file(rss_file, output)
	'''

class Library:
	def __init__(self):
		self.categories = CategoryList()
		self.pages = PageList()
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

	def write_page(self, path):
		page_file = path_join(path, specs.DATA_FILE)
		if os.path.exists(page_file):
			raise PageExistsError('Page {!r} already exists.'.format(path))
		if not os.path.exists(path):
			os.makedirs(path)
		scriber = MechaniScribe()
		model_page_file = path_join(specs.DATA_DIR, specs.DATA_FILE)
		content = book_dweller.bring_file(model_page_file)
		date = datetime.today().strftime(specs.DATE_FORMAT)
		scriber.write_file(page_file, content.format(date))
	
	def get_pages(self, path):
		scriber = MechaniScribe(self.meta)
		scriber.read_page_tree(path)
		return scriber.page_list

'''
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
'''
