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

import utils
from templex import TemplateParser
from exceptions import (ValuesNotDefinedError, FileNotFoundError,
						SiteAlreadyInstalledError, PageExistsError,
						PageValueError, TemplateError)

# aliases
regex_replace = re.sub
path_join = os.path.join
isdir = os.path.isdir
basename = os.path.basename
listdir = os.listdir

# Configuration values
DATA_FILE = 'page.me'
CONFIG_FILE = 'config.me'
TEMPLATES_DIR = 'templates'
TEMPLATES_EXT = 'tpl'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
JSON_FILENAME = 'data.json'
HTML_FILENAME = 'index.html'

# Setting values based on config
script_path = os.path.dirname(os.path.abspath(__file__))
data_dir = path_join(script_path, 'data')

MODEL_FEED_FILE = path_join(data_dir, 'feed.tpl')
MODEL_CONFIG_FILE = path_join(data_dir, CONFIG_FILE)
MODEL_DATA_FILE = path_join(data_dir, DATA_FILE)
MODEL_TEMPLATES_DIR = path_join(data_dir, TEMPLATES_DIR)


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
		self.paginate()


class CategoryList:
	def __init__(self):
		self.categories = {}

	def __iter__(self):
		for category in self.categories.values():
			yield category

	def add_category(self, category_name):
		if category_name in self.categories.keys() or not category_name:
			return
		self.categories[category_name] = Category(category_name)

	def add_page(self, category_name, page):
		if category_name not in self.categories.keys() or not category_name:
			return
		self.categories[category_name].add_page(page)


class Category:
	def __init__(self, name):
		self.name = name
		self.pages = PageList()
		self.pages.pagination = True

	def add_page(self, page):
		self.pages.insert(page)


class ContentRenderer():
	def __init__(self, template):
		self.template = self.read_template(template)

	def read_template(self, tpl_filename):
		'''Returns a template string from the template folder'''
		tpl_filepath = path_join(TEMPLATES_DIR, tpl_filename)
		if not os.path.exists(tpl_filepath):
			raise FileNotFoundError('Template {!r} not found'.format(tpl_filename))
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


class Content:
	def initialize(self, params):
		''' Set properties dynamically '''
		required_keys_cache = list(self.required_keys)
		for key in params.keys():
			method_name = 'set_{}'.format(key)
			if hasattr(self, method_name):
				getattr(self, method_name)(params[key])
			else:
				setattr(self, key, params[key])
			if key in required_keys_cache:
				required_keys_cache.remove(key)
		if len(required_keys_cache):
			raise ValuesNotDefinedError('The following values were not defined: {!r}'
			.format(', '.join(required_keys_cache)))
		del self.required_keys


class Page(Content):
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
		if not key in self.data:
			return None
		return self.data[key]
		
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
		utils.write_file(path_join(self.path, JSON_FILENAME), output)

	def generate_html(self, env):
		if 'nohtml' in self.props:
			return
		renderer = HTMLRenderer(self.template)
		output = renderer.render(self, env)
		utils.write_file(path_join(self.path, HTML_FILENAME), output)

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


class Site(Content):
	def __init__(self):
		self.required_keys = ('title', 'default_template', 'feed_dir', 'base_url')
		self.config_path = path_join(os.getcwd(), CONFIG_FILE)
		self.categories = CategoryList()
		self.pages = PageList()

	def load_config(self):
		if not os.path.exists(self.config_path):
			raise FileNotFoundError("Site is not installed!")
		config = utils.parse_input_file(utils.read_file(self.config_path))
		self.initialize(config)

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

	def read_page(self, path):
		'''Return the page data specified by path'''
		file_path = path_join(path, PAGE_FILE)
		if os.path.exists(file_path):
			return utils.parse_input_file(utils.read_file(file_path))
		return

	def build_page(self, path, page_data):
		'''Page object factory'''
		page = Page()
		page.path = regex_replace(r'^\.$|\./|\.\\', '', path)
		page.slug = basename(page.path)
		page.permalink = utils.urljoin(self.base_url, page.path)
		try:
			page.initialize(page_data)
		except ValuesNotDefinedError as e:
			raise ValuesNotDefinedError('{} at page {!r}'.format(e, path))
		if not page.template:
			page.template = self.default_template
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
			self.pages.insert(page)
		for subpage_path in self.read_subpages_list(path):
			self.read_page_tree(subpage_path, page)

	def read_subpages_list(self, path):
		'''Return a list containing the full path of the subpages'''
		subpages = []
		for folder in listdir(path):
			fullpath = path_join(path, folder)
			if isdir(fullpath):
				subpages.append(fullpath)
		return subpages

	def create(self):
		if os.path.exists(self.config_path):
			raise SiteAlreadyInstalledError("Site already installed!")
		if not os.path.exists(TEMPLATES_DIR):
			# copy the templates folder
			shutil.copytree(MODEL_TEMPLATES_DIR, TEMPLATES_DIR)
		if not os.path.exists(CONFIG_FILE):
			# copy the config file
			shutil.copyfile(MODEL_CONFIG_FILE, CONFIG_FILE)

	def create_page(self, path):
		if not os.path.exists(self.config_path):
			raise FileNotFoundError("Site is not installed!")
		if not os.path.exists(path):
			os.makedirs(path)
		dest_file = path_join(path, DATA_FILE)
		if os.path.exists(dest_file):
			raise PageExistsError("Page {!r} already exists!".format(dest_file))
		content = utils.read_file(MODEL_DATA_FILE)
		date = datetime.today().strftime(DATE_FORMAT)
		# need to write file contents to insert creation date
		utils.write_file(dest_file, content.format(date))

	def generate_feeds(self):
		renderer = RSSRenderer(MODEL_FEED_FILE)
		feed_dir = self.feed_dir
		if not os.path.exists(feed_dir):
			os.makedirs(feed_dir)
		env = { 'site': self }
		# generate feeds based on categories
		for cat in self.categories:
			fname = '{}.xml'.format(cat.name)
			env['feed'] = {
				'link': utils.urljoin(self.base_url, feed_dir, fname),
				'build_date': datetime.today()
			}
			page_list =  [p for p in cat.pages if p.is_feed_enabled()]
			page_list.reverse()
			env['pages'] = page_list[:self.feed_num]
			output = renderer.render(env)
			rss_file = path_join(feed_dir, fname)
			print("Generated {!r}.".format(rss_file))
			utils.write_file(rss_file, output)
