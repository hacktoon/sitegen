# coding: utf-8

'''
===============================================================================
Ion - A shocking simple static (site) generator

Author: Karlisson M. Bezerra
E-mail: contact@hacktoon.com
URL: https://github.com/hacktoon/ion
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


def urljoin(base, *slug):
	'''Custom URL join function to concatenate and add slashes'''
	fragments = [base]
	fragments.extend(filter(None, slug))
	return '/'.join(s.strip('/') for s in fragments)


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


def extract_multivalues(tag_string):
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
	return parse_ion_file(read_file(config_path))


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


def convert_page_date(page_data):
	date = page_data.get('date')
	if date:
		try:
			# converts date string to datetime object
			date = datetime.strptime(date, config.DATE_FORMAT)
		except ValueError:
			sys.exit('Zap! Wrong date format detected at {!r}!'.format(data_file))
	else:
		date = datetime.now()
	return date


def process_group_data(page_data):
	group_data = {}
	keys = [k for k in page_data.keys() if k.startswith('group_')]
	if 'group' in page_data['props']:
		group_data['group'] = os.path.basename(page_data['path'])
	for key in keys:
		group_data[key.replace('group_', '')] = page_data[key]
	return group_data


def get_page_data(env, path):
	'''Returns a dictionary with the page data'''
	#removing '.' of the path in the case of root directory of site
	data_file = os.path.join(path, config.DATA_FILE)
	# avoid directories that doesn't have a data file
	if not os.path.exists(data_file):
		return
	page_data = parse_ion_file(read_file(data_file))
	page_data['path'] = path
	page_data['date'] = convert_page_date(page_data)
	# absolute link of the page
	page_data['permalink'] = urljoin(env['base_url'], path)
	# splits tags into a list
	page_data['tags'] = extract_multivalues(page_data.get('tags'))
	# get the page properties
	page_data['props'] = extract_multivalues(page_data.get('props'))
	group_data = process_group_data(page_data)
	if group_data:
		page_data['group_data'] = group_data
	return page_data


def get_page_children(env, path, folders):
	'''Returns a list containing the full path of the children pages,
	removing the ignored pages like the themes folder'''
	join = os.path.join
	isdir = os.path.isdir
	children = []
	for folder in folders:
		fullpath = join(path, folder)
		if isdir(fullpath) and fullpath not in env['ignore_folders']:
			children.append(fullpath)
	return children


def apply_group_data(page_data, group_data):
	'''Add the group properties to the page, if it isn't already
	present. The page data has priority.'''
	if not group_data:
		return
	for key in group_data.keys():
		# already defined, so do not override
		if key in page_data:
			continue
		page_data[key] = group_data[key]


def read_page_files(env, path, group_data=None):
	'''Read the folders recursively and creates a dictionary
	containing the pages' data.'''
	# inherits the group defined previously, if it exists
	current_group_data = group_data or {}
	file_list = os.listdir(path)
	# removing dot from path
	path = re.sub(r'^\.$|\./|\.\\', '', path)
	children = get_page_children(env, path, file_list)
	
	# there's a data file in this path
	if os.path.exists(os.path.join(path, config.DATA_FILE)):
		page_data = get_page_data(env, path)
		# merge in the group properties defined in parent page
		apply_group_data(page_data, current_group_data)
		# stores the path of its children
		page_data['children'] = children
		# if this page defines a group, pass it to children pages
		# register it in the environment for feed generation
		if 'group_data' in page_data:
			current_group_data = page_data['group_data']
			# set the group name to page properties for sorting later
			env['groups'].append(current_group_data['group'])
		env['pages'][path] = page_data

	# process the children pages, pass the group data if defined
	for child_path in children:
		read_page_files(env, child_path, current_group_data)


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


def get_env():
	'''Returns a dict containing the site data'''
	env = get_site_config()
	if not env:
		sys.exit('Zap! Ion is not installed in this folder!')
	base_url = env.get('base_url')
	if not base_url:
		sys.exit('Zap! base_url was not set in config!')
	# add a trailing slash to base url, if necessary
	env['base_url'] = urljoin(base_url, '/')
	env['themes_url'] = urljoin(env['base_url'], config.THEMES_DIR)
	env['site_tags'] = extract_multivalues(env.get('site_tags'))
	env['feed_sources'] = extract_multivalues(env.get('feed_sources'))
	env['ignore_folders'] = [config.THEMES_DIR, env.get('feed_dir')]
	env['pages'] = {}
	env['groups'] = []
	env['feeds'] = []
	# now let's read all the pages and groups from files 
	read_page_files(env, os.curdir)
	paginate_groups(env)
	return env


def dataset_filter_group(dataset, group_name):
	if not group_name:
		return dataset
	from_group = lambda page: page.get('group') == group_name
	dataset = [page for page in dataset if from_group(page)]
	return dataset


def dataset_sort(dataset, field_sort, order='asc'):
	reverse = (order == 'desc')
	# all pages have a date, even if not specified in data files
	sort_by = lambda page: page[field_sort]
	dataset = sorted(dataset, key=sort_by, reverse=reverse)
	return dataset


def dataset_range(dataset, num_range):
	if not num_range:
		return dataset
	# if an integer was passed, returns a slice
	try:
		num = int(num_range)
		return dataset[:num]
	except ValueError:
		pass
	# limit number of objects to show
	start, end = num_range.partition(':')[::2]
	try:
		start = abs(int(start)) if start else 0
		end = abs(int(end)) if end else None
	except ValueError:
		sys.exit('Zap! [{}, {}] Bad range argument!'.format(start, end))
	if ':' in num_range:
		return dataset[start:end]
	else: # a single number means quantity of posts
		return dataset[:start]


def apply_page_filters(pages, args):
	pages = [p for p in pages if not 'nolist' in p.get('props', [])]
	# must limit the group first
	pages = dataset_filter_group(pages, args.get('group'))
	# listing order
	pages = dataset_sort(pages, args.get('sort', 'date'), args.get('ord'))
	# number must be the last one
	pages = dataset_range(pages, args.get('num'))
	return pages


def query_pages(env, page, args):
	'''Make queries to the environment data set'''
	src = args.get('src', '')
	sources = ['pages', 'feeds', 'children']
	# calling the proper query function
	if not src in sources:
		sys.exit('Zap! "src" argument is'
		' missing or invalid!'.format(src))
	if src == 'feeds':
		# feeds are already sorted and filtered
		return env['feeds']
	if src == 'pages':
		dataset = list(env['pages'].values())
	elif src == 'children':
		pages = page.get('children', [])
		dataset = [env['pages'][p] for p in pages if p in env['pages']]
	return apply_page_filters(dataset, args)
