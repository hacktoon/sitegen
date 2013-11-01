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
import sys
import re
import shutil
from datetime import datetime

from exceptions import *
from templex import TemplateParser
from renderers import (JSONRenderer, RSSRenderer, HTMLRenderer)

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
# format in which the date will be stored
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
JSON_FILENAME = 'data.json'
HTML_FILENAME = 'index.html'

# Regex pattern to remove the dot from file pathname
PATH_DOT_PATTERN = r'^\.$|\./|\.\\'

# Setting values based on config
script_path = os.path.dirname(os.path.abspath(__file__))
data_dir = path_join(script_path, 'data')

MODEL_FEED_FILE = path_join(data_dir, 'feed.tpl')
MODEL_CONFIG_FILE = path_join(data_dir, CONFIG_FILE)
MODEL_DATA_FILE = path_join(data_dir, DATA_FILE)
MODEL_TEMPLATES_DIR = path_join(data_dir, TEMPLATES_DIR)



def urljoin(base, *slug):
	'''Custom URL join function to concatenate and add slashes'''
	fragments = [base]
	fragments.extend(filter(None, slug))
	return '/'.join(s.strip('/') for s in fragments)

def read_file(path):
	if not os.path.exists(path):
		sys.exit('File {!r} couldn\'t be found!'.format(path))
	with open(path, 'r') as f:
		return f.read()

def write_file(path, content=''):
	with open(path, 'w') as f:
		f.write(content)

def parse_input_file(file_string):
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

def extract_multivalues(tag_string):
	'''Converts a comma separated list of tags into a list'''
	tag_list = []
	if tag_string:
		tags = tag_string.strip(',').split(',')
		tag_list = [tag.strip() for tag in tags]
	return tag_list

'''
# if any required key wasn't set, raise exception
if len(required_keys):
	raise ValuesNotDefinedError('The following values were not defined: {!r}'
	.format(', '.join(required_keys)))
'''

class Group:
	def __init__(self, name):
		self.name = name
		self.pages = {}  # stores pages indexed by its path

	def add_page(self, page):
		self.pages.append(page)

	def page_data(self, page):
		return {
			'title': page.title,
			'permalink': page.permalink
		}

	def paginate(self, site):
		'''Set the pagination info for the pages'''		
		length = len(self.pages)
		for index, page in enumerate(self.pages):
			page.first = self.page_data(pages[0])
			next_index = index + 1 if index < length - 1 else -1
			page.next = self.page_data(pages[next_index])
			prev_index = index - 1 if index > 0 else 0
			page.prev = self.page_data(pages[prev_index])
			page.last = self.page_data(pages[-1])


class Page:
	def __init__(self):
		self.required_keys = ('title', 'date')
		self.template = ''
		self.props = []
		self.parent = None
		self.group = ''
		self.styles = ''
		self.scripts = ''
		self.meta = {}

	def set_template(self, template):
		self.template = template

	def set_tags(self, tags):
		self.tags = extract_multivalues(tags)

	def set_props(self, props):
		self.props = extract_multivalues(props)

	def set_styles(self, styles):
		self.styles = extract_multivalues(styles)

	def set_scripts(self, scripts):
		self.scripts = extract_multivalues(scripts)

	def is_draft(self):
		return 'draft' in self.props
	
	def is_group(self):
		return 'group' in self.props

	def is_html_enabled(self):
		return 'nohtml' not in self.props

	def is_json_enabled(self):
		return 'nojson' not in self.props
		
	def set_date(self, date):
		'''converts date string to datetime object'''
		if date:
			try:
				self.date = datetime.strptime(date, DATE_FORMAT)
			except ValueError:
				sys.exit('Wrong date format '
				'detected at {!r}!'.format(self.path))
		else:
			self.date = datetime.now()
	
	def generate_json(self):
		if not self.is_json_enabled():
			return
		output = JSONRenderer().render(self)
		write_file(path_join(self.path, JSON_FILENAME), output)

	def generate_html(self, page):
		if not page.is_html_enabled():
			return
		renderer = HTMLRenderer()
		output = renderer.render(page)
		write_file(path_join(page._path, HTML_FILENAME), output)
	
	def render(self, env):
		self.generate_json()
		self.generate_html(env)


class Site():
	def __init__(self):
		self.required_keys = ('title', 'default_template', 'feed_dir', 'base_url')
		self.config_path = path_join(os.getcwd(), CONFIG_FILE)
		self.groups = {}
		self.pages = []

	def set_base_url(self, base_url):
		if not base_url:
			sys.exit('base_url was not set in config!')
		# add a trailing slash to base url, if necessary
		self.base_url = urljoin(base_url, '/')

	def set_tags(self, tags):
		self.tags = extract_multivalues(tags)

	def set_feed_num(self, feed_num):
		try:
			self.feed_num = int(feed_num)
		except ValueError:
			self.feed_num = 8

	def set_default_template(self, template):
		self.default_template = template

	def set_ignore_folders(self, folders):
		self.ignore_folders = extract_multivalues(folders)
		'''
		ignore_folders.extend([TEMPLATES_DIR, config.get('feed_dir')])
		self.ignore_folders = ignore_folders'''

	def load_config(self):
		if not os.path.exists(self.config_path):
			raise FileNotFoundError()
		config = parse_input_file(read_file(self.config_path))

	def create(self):
		if os.path.exists(self.config_path):
			raise SiteAlreadyInstalledError()
		# copy the templates folder
		shutil.copytree(MODEL_TEMPLATES_DIR, TEMPLATES_DIR)
		# copy the config file
		shutil.copyfile(MODEL_CONFIG_FILE, CONFIG_FILE)

	def read_page(self, path):
		'''Return the page data specified by path'''
		data_file = path_join(path, DATA_FILE)
		# avoid directories that don't have a data file
		if not os.path.exists(data_file):
			return
		return parse_input_file(read_file(data_file))

	def write_page(self, path):
		if not os.path.exists(path):
			os.makedirs(path)
		# full path of page data file
		dest_file = path_join(path, DATA_FILE)
		if os.path.exists(dest_file):
			raise PageExistsError()
		# copy the model page data file to a new file
		content = read_file(MODEL_DATA_FILE)
		# saving date in the format configured
		date = datetime.today().strftime(DATE_FORMAT)
		# need to write file contents to insert creation date
		write_file(dest_file, content.format(date))

	def build_page(self, path, parent, page_data):
		'''Page object factory'''
		page = Page()
		page.path = regex_replace(PATH_DOT_PATTERN, '', path)
		page.permalink = urljoin(self.base_url, page.path)
		page.parent = parent
		try:
			page.initialize(page_data)
		except ValuesNotDefinedError as e:
			sys.exit(e)
		# the parent page template has precedence
		if not page.template:
			if page.parent:
				page.template = page.parent.template
			else:
				page.template = self.default_template
		# creating group
		if page.is_group():
			group_name = basename(page.path)
			if group_name not in self.groups.keys():
				self.groups[group.name] = Group(group_name)
		# setting page group
		if page.parent:
			if page.parent.is_group():
				page.group = os.path.basename(page.parent.path)
			else:
				page.group = page.parent.group
		if page.group:
			self.groups[page.group].add_page(page)
		return page

	def insert_page(self, page):
		'''Insert page in list ordered by date'''
		index = self.pages
		count = 0
		while True:
			if count == len(index) or page.date <= index[count].date:
				index.insert(count, page)
				break
			count += 1

	def read_page_tree(self, path, parent=None):
		'''Read the folders recursively and create an ordered list
		of page objects.'''
		page_data = self.read_page(path)
		page = None
		if page_data:
			page = self.build_page(path, parent, page_data)
			self.insert_page(page)
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

	def generate(self):
		self.read_page_tree(os.curdir)
		for group in self.groups:
			group.paginate()
		for page in self.pages:
			if page.is_draft():
				continue
			page.render(env)

	def write_feed_file(env, filename):
		feed_dir = env.get('feed_dir', 'feed')
		feed_data = {
			'description': env.get('site_description'),
			'build_date': datetime.today()  # sets lastBuildDate
		}
		# create the feed directory
		if not os.path.exists(feed_dir):
			os.makedirs(feed_dir)
		feed_tpl = axiom.read_file(MODEL_FEED_FILE)
		feed_data['link'] = urljoin(env['base_url'], feed_dir, filename)
		feed_content = render_template(feed_tpl, env, feed_data)
		feed_path = path_join(feed_dir, filename)
		axiom.write_file(feed_path, feed_content)
		if env['output_enabled']:
			print('Feed {!r} generated.'.format(feed_path))
	
	'''
	def generate_feeds(self, env):
		sources = env.get('feed_sources')
		if not sources:
			print('No feeds generated.')
			return
		pages = env['pages'].values()
		# filtering the pages that shouldn't be listed in feeds
		pages = axiom.dataset_filter_props(pages, ['draft', 'nofeed'])

		if 'all' in sources:
			# copy the list
			set_feed_source(env, list(pages))
			write_feed_file(env, 'default.xml')
		if 'group' in sources:
			for group_name in env['groups']:
				# copy the list each iteration
				group_pages = axiom.dataset_filter_group(list(pages), group_name)
				set_feed_source(env, group_pages)
				write_feed_file(env, '{}.xml'.format(group_name))
	'''
