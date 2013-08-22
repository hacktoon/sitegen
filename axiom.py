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


# Configuration values
DATA_FILE = 'page.me'
CONFIG_FILE = 'config.me'
TEMPLATES_DIR = 'templates'
DEFAULT_TEMPLATE = 'main.tpl'
# format in which the date will be stored
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

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
	def __init__(self, path):
		self.path = path
	
	def create(self, title):
		'''Creates a data.ion file in the folder passed as parameter'''
		if not get_site_config():
			sys.exit('Mnemonix is not installed!')
		if not os.path.exists(path):
			os.makedirs(path)
		# full path of page data file
		dest_file = os.path.join(path, DATA_FILE)
		if os.path.exists(dest_file):
			sys.exit('Page {!r} already exists.'.format(path))
		# copy the skel page data file to new page
		content = read_file(MODEL_DATA_FILE)
		# saving date in the format configured
		date = datetime.today().strftime(DATE_FORMAT)
		# need to write file contents to insert creation date
		write_file(dest_file, content.format(date))
		return dest_file
	
	def load(self, params):
		self.date = self.convert_date(params['date'])
		# absolute link of the page
		self.permalink = urljoin(env['base_url'], path)
		# splits tags into a list
		self.tags = extract_multivalues(params.get('tags'))
		# get the page properties
		self.props = extract_multivalues(params.get('props'))
		# register group in the environment for feed generation
		if 'group' in self.props:
			group_name = os.path.basename(path)
			env['groups'].append(group_name)
	
	def convert_date(self, page_data):
		date = page_data.get('date')
		if date:
			try:
				# converts date string to datetime object
				date = datetime.strptime(date, DATE_FORMAT)
			except ValueError:
				sys.exit('Wrong date format detected at {!r}!'.format(data_file))
		else:
			date = datetime.now()
		return date
	
	def to_json(env, page):
		page = page.copy()
		page['date'] = date_to_string(page['date'])
		json_filepath = os.path.join(page['path'], 'index.json')
		write_file(json_filepath, json.dumps(page))

	def to_html(env, page):
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
		if not os.path.exists(config_path):
			raise ConfigNotFoundException()
		self.config = parse_input_file(read_file(config_path))

	def create(self):
		if os.path.exists(self.config_path):
			raise SiteAlreadyInstalledException()
		# copy the templates folder
		shutil.copytree(MODEL_TEMPLATES_DIR, TEMPLATES_DIR)
		# copy the config file
		shutil.copyfile(MODEL_CONFIG_FILE, CONFIG_FILE)

	def load(self):
		'''Returns a dict containing the site data'''
		config = self.load_config()
		self.env = {}
		if not config.get('base_url'):
			sys.exit('base_url was not set in config!')
		
		# add a trailing slash to base url, if necessary
		env['site_tags'] = extract_multivalues(env.get('site_tags'))
		env['feed_sources'] = extract_multivalues(env.get('feed_sources'))
		ignore_folders = extract_multivalues(env.get('ignore_folders'))
		ignore_folders.extend([TEMPLATES_DIR, env.get('feed_dir')])
		env['ignore_folders'] = ignore_folders
		env['pages'] = {}
		env['groups'] = []
		env['feeds'] = []
		# now let's read all the pages and groups from files 
		read_page_files(env, os.curdir)
		paginate_groups(env)
		return env

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


class Database():
	def __init__(self):
		pass
	
	def read_page(self, env, path):
		'''Returns a dictionary with the page data'''
		#removing '.' of the path in the case of root directory of site
		data_file = os.path.join(path, DATA_FILE)
		# avoid directories that doesn't have a data file
		if not os.path.exists(data_file):
			return
		page_data = parse_input_file(read_file(data_file))
		page = Page(path)
		page.load(page_data)
		return page
	
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
		return pages
	
	def read(self, env, path, parent=None):
		'''Read the folders recursively and creates a dictionary
		containing the pages' data.'''
		file_list = os.listdir(path)
		page_data = None
		# removing dot from path
		path = re.sub(r'^\.$|\./|\.\\', '', path)
		children = get_page_children(env, path, file_list)

		# there's a data file in this path
		if os.path.exists(os.path.join(path, DATA_FILE)):
			page_data = self.read_page(env, path)
			# inherit the template from parent, if not defined its own
			if 'template' not in page_data:
				template = env.get('default_template', DEFAULT_TEMPLATE)
				if parent:
					template = parent.get('template', template)
				page_data['template'] = template
			# stores the path of its children
			page_data['children'] = children
			env['pages'][path] = page_data

		# process the children pages, passing the parent page
		for child_path in children:
			self.read(env, child_path, page_data)


	def get_page_children(self, env, path, folders):
		'''Returns a list containing the full path of the children pages,
		removing the ignored folders like templates'''
		join = os.path.join
		isdir = os.path.isdir
		children = []
		for folder in folders:
			fullpath = join(path, folder)
			if isdir(fullpath) and fullpath not in env['ignore_folders']:
				children.append(fullpath)
		return children


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
