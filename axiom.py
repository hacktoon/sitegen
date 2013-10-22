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
import json
import shutil
from datetime import datetime
from templex import TemplateParser

# aliases
regex_replace = re.sub
path_join = os.path.join

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


class FileNotFoundError(Exception):
	def __init__(self, msg):
		self.msg = msg
	def __str__(self):
		return self.msg


class SiteAlreadyInstalledError(Exception):
	def __init__(self, msg):
		self.msg = msg
	def __str__(self):
		return self.msg


class PageExistsError(Exception):
	def __init__(self, msg):
		self.msg = msg
	def __str__(self):
		return self.msg


class ValuesNotDefinedError(Exception):
	def __init__(self, msg):
		self.msg = msg
	def __str__(self):
		return self.msg


def urljoin(base, *slug):
	'''Custom URL join function to concatenate and add slashes'''
	fragments = [base]
	fragments.extend(filter(None, slug))
	return '/'.join(s.strip('/') for s in fragments)

def date_to_string(date, fmt=None):
	if not fmt:
		fmt = DATE_FORMAT
	return date.strftime(fmt)

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

def read_template(tpl_filename):
	'''Returns a template string from the template folder'''
	if not tpl_filename.endswith('.tpl'):
		tpl_filename = '{0}.tpl'.format(tpl_filename)
	tpl_filepath = path_join(TEMPLATES_DIR, tpl_filename)
	if not os.path.exists(tpl_filepath):
		raise FileNotFoundError()
	return read_file(tpl_filepath)

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
	feed_data['link'] = axiom.urljoin(env['base_url'], feed_dir, filename)
	feed_content = render_template(feed_tpl, env, feed_data)
	feed_path = path_join(feed_dir, filename)
	axiom.write_file(feed_path, feed_content)
	if env['output_enabled']:
		print('Feed {!r} generated.'.format(feed_path))

def set_feed_source(env, pages):
	items_listed = int(env.get('feed_num', 8))  # default value
	pages = axiom.dataset_sort(pages, 'date', 'desc')
	pages = axiom.dataset_range(pages, items_listed)
	env['feeds'] = pages


class ContentRenderer():
	def __init__(self, template):
		self.template = template

	def render(self):
		pass


class JSONRenderer(ContentRenderer):
	def __init__(self):
		pass

	def render(self, page):
		page_dict = page.serialize()
		page_dict['date'] = date_to_string(page_dict['date'])
		return json.dumps(page_dict)


class RSSRenderer(ContentRenderer):
	def render(self, page_dict):
		pass


class HTMLRenderer(ContentRenderer):
	def build_external_tags(self, links, tpl):
		tag_list = []
		for link in links:
			tag_list.append(tpl.format(link))
		return '\n'.join(tag_list)

	def build_style_tags(self, links):
		if not links:
			return ''
		tpl = '<link rel="stylesheet" type="text/css" href="{0}"/>'
		links = [f for f in links if f.endswith('.css')]
		return self.build_external_tags(links, tpl)

	def build_script_tags(self, links):
		if not links:
			return ''
		tpl = '<script src="{0}"></script>'
		links = [f for f in links if f.endswith('.js')]
		return self.build_external_tags(links, tpl)

	def render(self, page):
		page_dict = page.serialize()
		page_dict['styles'] = self.build_style_tags(page._styles)
		page_dict['scripts'] = self.build_script_tags(page._scripts)
		print(page_dict)
		return ''
		#renderer = TemplateParser(self.template)
		#return renderer.render(page_dict)


class Serializable:
	def initialize(self, params):
		# define properties dynamically
		required_keys = list(self._required_keys)

		for key in params.keys():
			method_name = 'set_{}'.format(key)
			# if setter method exists, call it
			if hasattr(self, method_name):
				getattr(self, method_name)(params[key])
			else:
				setattr(self, key, params[key])
			if key in required_keys:
				required_keys.remove(key)
		# if any required key wasn't set, raise exception
		if len(required_keys):
			raise ValuesNotDefinedError('The following values were not defined: {!r}'
			.format(', '.join(required_keys)))

	def serialize(self):
		# convert an object to a dict
		params = vars(self).items()
		# ignore protected attributes (starting with '_')
		return {k:v for k,v in params if not k.startswith('_')}


class Page(Serializable):
	def __init__(self):
		self._required_keys = ('title', 'date', 'content')
		self._template = ''
		self._props = []
		self._parent = None
		self._group = ''
		self._styles = ''
		self._scripts = ''

	def set_template(self, template):
		self._template = template

	def set_date(self, date):
		'''converts date string to datetime object'''
		if date:
			try:
				date = datetime.strptime(date, DATE_FORMAT)
			except ValueError:
				sys.exit('Wrong date format '
				'detected at {!r}!'.format(self.path))
		else:
			date = datetime.now()
		self.date = date

	def set_tags(self, tags):
		self.tags = extract_multivalues(tags)

	def set_props(self, props):
		self._props = extract_multivalues(props)

	def set_styles(self, styles):
		self._styles = extract_multivalues(styles)

	def set_scripts(self, scripts):
		self._scripts = extract_multivalues(scripts)

	def is_draft(self):
		return 'draft' in self._props
	
	def is_group(self):
		return 'group' in self._props

	def is_html_enabled(self):
		return 'nohtml' not in self._props

	def is_json_enabled(self):
		return 'nojson' not in self._props


class Site(Serializable):
	def __init__(self):
		self._required_keys = ('title', 'default_template', 'feed_dir', 'base_url')
		self._config_path = path_join(os.getcwd(), CONFIG_FILE)
		self._page_list = []
		self._groups = []

	def set_base_url(self, base_url):
		if not base_url:
			sys.exit('base_url was not set in config!')
		# add a trailing slash to base url, if necessary
		self.base_url = urljoin(base_url, '/')

	def set_tags(self, tags):
		self.tags = extract_multivalues(tags)
	
	def set_default_template(self, template):
		self._default_template = template

	def set_ignore_folders(self, folders):
		ignore_folders = extract_multivalues(folders)
		'''
		ignore_folders.extend([TEMPLATES_DIR, config.get('feed_dir')])
		self.ignore_folders = ignore_folders'''

	def load_config(self):
		if not os.path.exists(self._config_path):
			raise FileNotFoundError()
		config = parse_input_file(read_file(self._config_path))
		self.initialize(config)

	def read_page(self, path):
		'''Return the page data specified by path'''
		data_file = path_join(path, DATA_FILE)
		# avoid directories that don't have a data file
		if not os.path.exists(data_file):
			return
		page_data = parse_input_file(read_file(data_file))
		return page_data

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

	def create(self):
		if os.path.exists(self.config_path):
			raise SiteAlreadyInstalledError()
		# copy the templates folder
		shutil.copytree(MODEL_TEMPLATES_DIR, TEMPLATES_DIR)
		# copy the config file
		shutil.copyfile(MODEL_CONFIG_FILE, CONFIG_FILE)

	def paginate_groups(self):
		'''Set the pagination info to the pages'''
		def _pagination_data(page):
			# internal function to build a pagination object
			return {
				'title': page.title,
				'permalink': page.permalink
			}
		for group in self._groups:
			pages = [p for p in self._page_list if p._group == group]
			length = len(pages)
			for index, page in enumerate(pages):
				page.first = _pagination_data(pages[0])
				page.last = _pagination_data(pages[-1])
				next_index = index + 1 if index < length - 1 else -1
				page.next = _pagination_data(pages[next_index])
				prev_index = index - 1 if index > 0 else 0
				page.prev = _pagination_data(pages[prev_index])

	def update_groups(self, page):
		'''Fill the groups definition list based on pages'''
		group = page._group
		if not group:
			return
		if group not in self._groups:
			self._groups.append(group)

	def insert_page(self, page):
		'''Insert page in list ordered by date'''
		index = self._page_list
		count = 0
		while True:
			if count == len(index) or page.date <= index[count].date:
				index.insert(count, page)
				break
			count += 1

	def read_page_children(self, path):
		'''Return a list containing the full path of the subpages'''
		isdir = os.path.isdir
		subpages = []
		for folder in os.listdir(path):
			fullpath = path_join(path, folder)
			if isdir(fullpath):
				subpages.append(fullpath)
		return subpages
	
	def build_page(self, page_data, path, parent):
		'''Page object factory'''
		page = Page()
		page._path = path
		page._parent = parent
		page_url = regex_replace(PATH_DOT_PATTERN, '', path)
		page.permalink = urljoin(self.base_url, page_url)
		try:
			page.initialize(page_data)
		except ValuesNotDefinedError as e:
			sys.exit(e)
		# setting page group
		if page._parent and page._parent.is_group():
			page._group = os.path.basename(page._parent._path)
		return page
	
	def read_page_tree(self, path, parent=None):
		'''Read the folders recursively and create an ordered list
		of page objects.'''
		page_data = self.read_page(path)
		page = None
		if page_data:
			page = self.build_page(page_data, path, parent)
			self.update_groups(page)
			self.insert_page(page)
		for subpage_path in self.read_page_children(path):
			self.read_page_tree(subpage_path, page)

	def get_pages(self, path):
		self.read_page_tree(path)
		self.paginate_groups()
		return self._page_list

	def generate_json(self, page):
		if not page.is_json_enabled():
			return
		output = JSONRenderer().render(page)
		write_file(path_join(page._path, JSON_FILENAME), output)

	def generate_html(self, page):
		if not page.is_html_enabled():
			return
		# the parent page's template has precedence
		if not page._template:
			if page._parent:
				page._template = page._parent._template
			else:
				page._template = self._default_template
		template = read_template(page._template)
		renderer = HTMLRenderer(template)
		output = renderer.render(page)
		write_file(path_join(page._path, HTML_FILENAME), output)

	def generate(self, page):
		if page.is_draft():
			return
		self.generate_json(page)
		self.generate_html(page)

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
