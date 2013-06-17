# coding: utf-8

'''
===============================================================================
Ion - A shocking simple static (site) generator

Author: Karlisson M. Bezerra
E-mail: contact@hacktoon.com
URL: https://github.com/karlisson/ion
License: WTFPL - http://sam.zoy.org/wtfpl/COPYING

===============================================================================
'''

import os
import sys
import re
import shutil
import time

from datetime import datetime

import config


required_config_keys = ['site_name', 'site_author',
	'site_description', 'base_url', 'default_theme']

required_page_keys = ['title', 'date', 'content']


def urljoin(base, slug):
	'''Custom URL join function to concatenate and add slashes'''
	return '/'.join(s.strip('/') for s in [base, slug])


def read_file(path):
	if not os.path.exists(path):
		sys.exit('Zap! File {!r} couldn\'t be found!'.format(path))
	with open(path, 'r') as f:
		return f.read()


def write_file(path, content=''):
	with open(path, 'w') as f:
		f.write(content)


def parse_ion_file(file_string):
	ion_data = {}
	lines = file_string.split('\n')
	for num, line in enumerate(lines):
		# avoids empty lines and comments
		line = line.strip()
		if not line or line.startswith('#'):
			continue
		if(line == 'content'):
			# read the rest of the file
			ion_data['content'] = ''.join(lines[num + 1:])
			break
		key, value = [l.strip() for l in line.split('=', 1)]
		ion_data[key] = value
	return ion_data


def keys_missing(keys, container):
	'''Checks for missing keys in a data container'''
	for key in keys:
		if not key in container:
			return key
	return False


def extract_tags(tag_string):
	'''Converts a comma separated list of tags into a list'''
	tag_list = []
	if tag_string:
		tags = tag_string.strip(',').split(',')
		tag_list = [tag.strip() for tag in tags]
	return tag_list


def read_html_template(theme_name, tpl_filename):
	'''Returns a HTML template string from the current theme folder'''
	theme_dir = os.path.join(config.THEMES_DIR, theme_name)
	if not tpl_filename.endswith('.tpl'):
		tpl_filename = '{0}.tpl'.format(tpl_filename)
	tpl_filepath = os.path.join(theme_dir, tpl_filename)
	if not os.path.exists(tpl_filepath):
		sys.exit('Zap! Template file {!r} '
				 'couldn\'t be found!'.format(tpl_filepath))
	return read_file(tpl_filepath)


def get_site_config():
	'''returns the current site config'''
	config_path = os.path.join(os.getcwd(), config.CONFIG_FILE)
	if not os.path.exists(config_path):
		return
	cfg = parse_ion_file(read_file(config_path))
	# check for missing keys
	key = keys_missing(required_config_keys, cfg)
	if key:
		sys.exit('Zap! The key {!r} is missing in site config!'.format(key))
	return cfg


def create_site():
	if get_site_config():
		sys.exit('Zap! Ion is already installed in this folder!')
	# copy the config file
	shutil.copyfile(config.MODEL_CONFIG_FILE, config.CONFIG_FILE)
	# copy the themes folder
	shutil.copytree(config.MODEL_THEMES_DIR, config.THEMES_DIR)


def create_page(path):
	'''Creates a data.ion file in the folder passed as parameter'''
	if not get_site_config():
		sys.exit('Zap! Ion is not installed!')
	if not os.path.exists(path):
		os.makedirs(path)
	# full path of page data file
	dest_file = os.path.join(path, config.DATA_FILE)
	if os.path.exists(dest_file):
		sys.exit('Zap! Page {!r} already exists.'.format(path))
	# copy the skel page data file to new page
	content = read_file(config.MODEL_DATA_FILE)
	# saving date in the format configured
	date = datetime.today().strftime(config.DATE_FORMAT)
	# need to write file contents to insert creation date
	write_file(dest_file, content.format(date))
	return dest_file


def get_page_data(env, path):
	'''Returns a dictionary with the page data'''
	#removing '.' of the path in the case of root directory of site
	data_file = os.path.join(path, config.DATA_FILE)
	# avoid directories that doesn't have a data file
	if not os.path.exists(data_file):
		return
	page_data = parse_ion_file(read_file(data_file))
	# verify missing required keys in page data
	key = keys_missing(required_page_keys, page_data)
	if key:
		sys.exit('Zap! The key {!r} is missing '
		'in page config at {!r}!'.format(key, path))
	# convert date string to datetime object
	date = page_data['date']
	try:
		page_data['date'] = datetime.strptime(date, config.DATE_FORMAT)
	except ValueError:
		sys.exit('Zap! Wrong date format detected at {!r}!'.format(data_file))
	# absolute link of the page
	page_data['permalink'] = urljoin(env['base_url'], path)
	# if a theme is not provided, uses default
	page_data['theme'] = page_data.get('theme', env['default_theme'])
	# splits tags into a list
	page_data['tags'] = extract_tags(page_data.get('tags'))
	page_data['path'] = path
	return page_data


def read_page_files(env):
	'''Returns all the pages created in the site'''
	pages = {}
	# running at the current dir
	for path, subdirs, filenames in os.walk('.'):
		# if did not find a data file, ignores
		if not config.DATA_FILE in filenames:
			continue
		# removing dot from path
		path = re.sub('^\.$|\./', '', path)
		page_data = get_page_data(env, path)
		# uses the page path as a key
		pages[path] = page_data
		# get the child pages
		page_data['children'] = []
		if path: # checks if isnt home page (empty string)
			# get parent folder to include itself as child page
			parent_path = os.path.dirname(path)
			# linking children pages, only if parent exists
			if parent_path in pages:
				pages[parent_path]['children'].append(path)
	return pages


def get_env():
	'''Returns a dict containing the site data'''
	env = get_site_config()
	if not env:
		sys.exit('Zap! Ion is not installed in this folder!')
	# add a trailing slash to base url, if necessary
	base_url = urljoin(env['base_url'], '/')
	env['base_url'] = base_url
	env['themes_url'] = urljoin(base_url, config.THEMES_DIR)
	#env['feed_url'] = urljoin(base_url, config.FEED_URL)
	env['site_tags'] = extract_tags(env.get('site_tags'))
	# now let's get all the pages
	env['pages'] = read_page_files(env)
	return env


def dataset_filter_category(dataset, cat=None):
	# FIXME - this may not work on windows - path/slug
	if not cat:
		return dataset
	from_cat = lambda c: c['path'].startswith(cat)
	dataset = [page for page in dataset if from_cat(page)]
	return dataset


def dataset_sort(dataset, sort, order):
	reverse = (order == 'desc')
	sort_by = lambda d: d[sort or 'date']
	return sorted(dataset, key=sort_by, reverse=reverse)


def dataset_range(dataset, num_range):
	if not dataset or not num_range:
		return dataset
	# limit number of objects to show
	start, end = num_range.partition(':')[::2]
	try:
		start = abs(int(start)) if start else 0
		end = abs(int(end)) if end else None
	except ValueError:
		sys.exit('Zap! Bad range argument!')
	if ':' in num_range:
		return dataset[start:end]
	else: # a single number means quantity of posts
		return dataset[:start]


def query_pages(env, page, dataset, args=None):
	if not dataset:
		return dataset
	# limit the category first
	dataset = dataset_filter_category(dataset, args.get('cat'))
	# listing order before number of objects
	dataset = dataset_sort(dataset, args.get('sort'), args.get('ord'))
	# number must be the last one
	dataset = dataset_range(dataset, args.get('num'))
	return dataset


def query(env, page, args):
	'''Make queries to the environment data set'''
	src = args.get('src', '')
	sources = {
		'pages': list(env['pages'].copy().values()),
		'children': [get_page_data(env, p) for p in page.get('children', [])]
	}
	# calling the proper query function
	if src in sources:
		return query_pages(env, page, sources[src], args)
	else:
		sys.exit('Zap! "src" argument is'
		' missing or invalid!'.format(src))
