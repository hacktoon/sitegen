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
import time
from datetime import datetime

# aliases
regex_replace = re.sub

# Configuration values
DATA_FILE = 'page.me'
CONFIG_FILE = 'config.me'
TEMPLATES_DIR = 'templates'
DEFAULT_TEMPLATE = 'main.tpl'
# format in which the date will be stored
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Regex pattern to remove the dot from file pathname
PATH_DOT_PATTERN = r'^\.$|\./|\.\\'

# Setting values based on config
script_path = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_path, 'data')

MODEL_FEED_FILE = os.path.join(data_dir, 'feed.tpl')
MODEL_CONFIG_FILE = os.path.join(data_dir, CONFIG_FILE)
MODEL_DATA_FILE = os.path.join(data_dir, DATA_FILE)
MODEL_TEMPLATES_DIR = os.path.join(data_dir, TEMPLATES_DIR)


class ConfigNotFoundException(Exception):
	pass

class SiteAlreadyInstalledException(Exception):
	pass

class PageExistsException(Exception):
	pass

class PageValuesNotDefined(Exception):
	def __init__(self, message):
		self.message = message
	def __str__(self):
		return self.message


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
	tpl_filepath = os.path.join(TEMPLATES_DIR, tpl_filename)
	if not os.path.exists(tpl_filepath):
		return ''
	return read_file(tpl_filepath)


def build_external_tags(filenames, permalink, tpl):
	tag_list = []
	for filename in filenames:
		url = axiom.urljoin(permalink, filename)
		tag_list.append(tpl.format(url))
	return '\n'.join(tag_list)


def build_style_tags(filenames, permalink):
	tpl = '<link rel="stylesheet" type="text/css" href="{0}"/>'
	filenames = axiom.extract_multivalues(filenames)
	filenames = [f for f in filenames if f.endswith('.css')]
	return build_external_tags(filenames, permalink, tpl)


def build_script_tags(filenames, permalink):
	tpl = '<script src="{0}"></script>'
	filenames = axiom.extract_multivalues(filenames)
	filenames = [f for f in filenames if f.endswith('.js')]
	return build_external_tags(filenames, permalink, tpl)



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
	feed_path = os.path.join(feed_dir, filename)
	axiom.write_file(feed_path, feed_content)
	if env['output_enabled']:
		print('Feed {!r} generated.'.format(feed_path))


def set_feed_source(env, pages):
	items_listed = int(env.get('feed_num', 8))  # default value
	pages = axiom.dataset_sort(pages, 'date', 'desc')
	pages = axiom.dataset_range(pages, items_listed)
	env['feeds'] = pages


class Page:
	def __init__(self, page_data):
		self.children = []
		mandatory_keys = ['path', 'title', 'date', 'content']
		for key in page_data.keys():
			method_name = 'set_{}'.format(key)
			if hasattr(self, method_name):
				getattr(self, method_name)(page_data[key])
			else:
				setattr(self, key, page_data[key])
			if key in mandatory_keys:
				mandatory_keys.remove(key)
		if len(mandatory_keys):
			raise PageValuesNotDefined('One or more page properties '
			'were not defined in {!r}: {!r}.'.format(page_data['path'],
			', '.join(mandatory_keys)))

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
		'''splits tags into a list'''
		self.tags = extract_multivalues(tags)

	def set_props(self, props):
		'''get the page properties'''
		self.props = extract_multivalues(props)

	def set_template(self, template):
		self.template = template

	# register group in the environment for feed generation
	#if 'group' in self.props:
		#group_name = os.path.basename(path)
		#env['groups'].append(group_name)


	def to_json(env, page):
		page = page.copy()
		page['date'] = date_to_string(page['date'])
		json_filepath = os.path.join(page['path'], 'index.json')
		write_file(json_filepath, json.dumps(page))

	def to_html(env, page):

		'''# inherit the template from parent, if not defined its own
		if 'template' in page_data:
			template = self.env.get('default_template', DEFAULT_TEMPLATE)
			if parent_page and parent_page.template:
				template = parent_page.template
			page.template = template'''

		page = page.copy()
		# get css and javascript found in the folder
		page['styles'] = build_style_tags(page.get('styles', ''), page['permalink'])
		page['scripts'] = build_script_tags(page.get('scripts', ''), page['permalink'])
		html_templ = read_template(page['template'])
		if not html_templ:
			sys.exit('Zap! Template file {!r} '
					 'couldn\'t be found for '
					 'page {!r}!'.format(page['template'], page['path']))

		# replace template with page data and listings
		html = render_template(html_templ, env, page)
		path = page['path']
		write_file(os.path.join(path, 'index.html'), html)
		if env['output_enabled']:
			print('"{0}" page generated.'.format(path or 'Home'))


class Site:
	def __init__(self):
		self.config_path = os.path.join(os.getcwd(), CONFIG_FILE)
		self.config = None
		self.env = {}

	def load_config(self):
		if not os.path.exists(self.config_path):
			raise ConfigNotFoundException()
		self.config = parse_input_file(read_file(self.config_path))

	def create_page(self, page):
		if not os.path.exists(self.config_path):
			raise ConfigNotFoundException()
		if not os.path.exists(page.path):
			os.makedirs(page.path)
		# full path of page data file
		dest_file = os.path.join(page.path, DATA_FILE)
		if os.path.exists(dest_file):
			raise PageExistsException()
		# copy the model page data file to a new file
		content = read_file(MODEL_DATA_FILE)
		# saving date in the format configured
		date = datetime.today().strftime(DATE_FORMAT)
		# need to write file contents to insert creation date
		write_file(dest_file, content.format(date))
		return dest_file

	def create(self):
		if os.path.exists(self.config_path):
			raise SiteAlreadyInstalledException()
		# copy the templates folder
		shutil.copytree(MODEL_TEMPLATES_DIR, TEMPLATES_DIR)
		# copy the config file
		shutil.copyfile(MODEL_CONFIG_FILE, CONFIG_FILE)

	def load(self):
		'''Loads the site's data into memory'''
		config = self.config
		env = {}
		if not config.get('base_url'):
			sys.exit('base_url was not set in config!')
		# add a trailing slash to base url, if necessary
		env['base_url'] = urljoin(config.get('base_url'), '/')
		self.tags = extract_multivalues(config.get('site_tags'))
		env['feed_sources'] = extract_multivalues(config.get('feed_sources'))
		ignore_folders = extract_multivalues(config.get('ignore_folders'))
		ignore_folders.extend([TEMPLATES_DIR, config.get('feed_dir')])
		env['ignore_folders'] = ignore_folders
		env['pages'] = []
		env['groups'] = []
		env['feeds'] = []
		# now let's read all the pages and groups from files
		db = Database()
		db.load(os.curdir)
		for p in db.query():
			print(vars(p))
		# TODO: check if path not in env['ignore_folders']
		#paginate_groups(env)
		self.env = env

	def generate(self):
		pass
		#page_data['permalink'] = urljoin(self.env['base_url'], path)

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


class Database:
	def __init__(self):
		self._page_index = []

	def load(self, path):
		self._build_index(path)

	def query(self):
		return self._page_index

	def _get_page_data(self, path):
		'''Return the page data specified by path'''
		# removing dot from path, including Windows path style
		path = regex_replace(PATH_DOT_PATTERN, '', path)
		data_file = os.path.join(path, DATA_FILE)
		# avoid directories that don't have a data file
		if not os.path.exists(data_file):
			return
		page_data = parse_input_file(read_file(data_file))
		page_data['path'] = path
		return page_data

	def _get_subpages_list(self, path):
		'''Return a list containing the full path of the subpages'''
		join, isdir = os.path.join, os.path.isdir
		subpages = []
		for folder in os.listdir(path):
			fullpath = join(path, folder)
			if isdir(fullpath):
				subpages.append(fullpath)
		return subpages

	def _build_index(self, path, parent_page=None):
		'''Read the folders recursively and create a list
		of page objects.'''
		page_data = self._get_page_data(path)
		if not page_data:
			return
		try:
			page = Page(page_data)
		except PageValuesNotDefined as e:
			sys.exit(e)
		page.parent = parent_page
		self._page_index.append(page)
		if parent_page:
			parent_page.children.append(page)
		for subpage_path in self._get_subpages_list(path):
			self._build_index(subpage_path, page)

	'''
	def dataset_filter_group(self, dataset, group_name):
		if not group_name:
			return dataset
		from_group = lambda page: page.get('group') == group_name
		dataset = [page for page in dataset if from_group(page)]
		return dataset

	def dataset_sort(self, dataset, field_sort, order='asc'):
		reverse = (order == 'desc')
		# all pages have a date, even if not specified in data files
		sort_by = lambda page: page[field_sort]
		dataset = sorted(dataset, key=sort_by, reverse=reverse)
		return dataset

	def dataset_filter_props(self, dataset, props):
		if not props:
			return dataset
		has_props = lambda p: any(x in p.get('props', []) for x in props)
		dataset = [page for page in dataset if not has_props(page)]
		return dataset

	def apply_page_filters(self, pages, args):
		# pages with these props will be filtered
		pages = dataset_filter_props(pages, ['draft', 'nolist'])
		# must limit the group first
		pages = dataset_filter_group(pages, args.get('group'))
		# listing order
		pages = dataset_sort(pages, args.get('sort', 'date'), args.get('ord'))
		return pages'''


def paginate_groups(env):
	groups = env['groups']
	key = 'permalink'
	for group in groups:
		pages = list(env['pages'].copy().values())
		pages = dataset_filter_group(pages, group)
		pages = dataset_sort(pages, 'date', 'desc')
		length = len(pages)
		for index, page in enumerate(pages):
			page['first'] = pages[0][key]
			page['last'] = pages[-1][key]
			next_index = index + 1 if index < length - 1 else -1
			page['next'] = pages[next_index][key]
			prev_index = index - 1 if index > 0 else 0
			page['prev'] = pages[prev_index][key]
