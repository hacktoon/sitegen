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

'''
	The wonder Mechaniscribe of the abissal library
'''
import os
import sys
import re

# aliases
path_join = os.path.join
isdir = os.path.isdir
basename = os.path.basename
listdir = os.listdir


def urljoin(base, *slug):
	'''Custom URL join function to concatenate and add slashes'''
	fragments = [base]
	fragments.extend(filter(None, slug))
	return '/'.join(s.replace('\\', '/').strip('/') for s in fragments)

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

def normalize(name):
	return name.replace(' ', '-').lower()

def read_page(path):
	'''Return the page data specified by path'''
	file_path = path_join(path, PAGE_FILE)
	if os.path.exists(file_path):
		return parse_input_file(read_file(file_path))
	return

def build_page(path, page_data):
	'''Page object factory'''
	page = Page()
	page.path = re.sub(r'^\.$|\./|\.\\', '', path)
	page.slug = basename(page.path)
	page.url = urljoin(base_url, page.path)
	try:
		page.initialize(page_data)
	except ValuesNotDefinedError as e:
		raise ValuesNotDefinedError('{} at page {!r}'.format(e, path))
	if not page.template:
		page.template = default_template
	return page

def read_page_tree(path, parent=None):
	'''Read the folders recursively and create an ordered list
	of page objects.'''
	page_data = read_page(path)
	page = None
	if page_data:
		page = build_page(path, page_data)
		page.parent = parent
		if parent:
			parent.add_child(page)
		# add page to ordered list of pages
		pages.insert(page)
	for subpage_path in read_subpages_list(path):
		read_page_tree(subpage_path, page)

def read_subpages_list(path):
	'''Return a list containing the full path of the subpages'''
	subpages = []
	for folder in listdir(path):
		fullpath = path_join(path, folder)
		if isdir(fullpath):
			subpages.append(fullpath)
	return subpages
	
def create():
	if os.path.exists(config_path):
		raise SiteAlreadyInstalledError("Site already installed!")
	if not os.path.exists(TEMPLATES_DIR):
		# copy the templates folder
		shutil.copytree(MODEL_TEMPLATES_DIR, TEMPLATES_DIR)
	if not os.path.exists(CONFIG_FILE):
		# copy the config file
		shutil.copyfile(MODEL_CONFIG_FILE, CONFIG_FILE)

def create_page(path):
	if not os.path.exists(config_path):
		raise FileNotFoundError("Site is not installed!")
	if not os.path.exists(path):
		os.makedirs(path)
	dest_file = path_join(path, DATA_FILE)
	if os.path.exists(dest_file):
		raise PageExistsError("Page {!r} already exists!".format(dest_file))
	content = read_file(MODEL_DATA_FILE)
	date = datetime.today().strftime(DATE_FORMAT)
	# need to write file contents to insert creation date
	write_file(dest_file, content.format(date))

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