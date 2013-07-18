# coding: utf-8

'''
==============================================================================
Ion - A shocking simple static (site) generator

Author: Karlisson M. Bezerra
E-mail: contact@hacktoon.com
URL: https://github.com/hacktoon/ion
License: WTFPL - http://sam.zoy.org/wtfpl/COPYING

==============================================================================
'''

import re
import os
import sys
import json
from datetime import datetime

import config
import quark


tag_exprs = (
	r'\{\{\s*(list)\s+(.+?)\s*\}\}(.+?)\{\{\s*end\s*\}\}',
	r'\{\{\s*(include)\s+([-a-z0-9]+)\s*\}\}',
	r'\{\{\s*(breadcrumbs)\s*\}\}(.+?)\{\{\s*end\s*\}\}',
	r'\{\{\s*([-a-z0-9_]+)(?:\s+(.*?))?\s*\}\}'
)


def date_to_string(date, fmt=None):
	if not fmt:
		fmt = config.DATE_FORMAT
	return date.strftime(fmt)


def parse_list_args(args):
	'''Parses parameters passed to list tag'''
	# expects 'src=pages num=5 cat=home/teste'
	arg_pairs = {}
	for arg in args.split():
		pair = arg.split('=', 1)
		if len(pair) == 2:
			key, value = pair
		else:
			sys.exit('Zap! List argument error at "{}"!'.format(args))
		arg_pairs[key] = value
	return arg_pairs


def parse_variable_args(args):
	'''Parses parameters passed to variable printint tags'''
	# expects 'fmt=etc | upper | capitalize
	arg_data = {}
	if not args:
		return arg_data
	args = args.strip('| ') # removes these chars from the edges
	args = [arg.strip() for arg in args.split('|')]
	for arg in args:
		if '=' in arg:
			cmd, val = arg.split('=', 1) # get first '=' only
			arg_data[cmd.strip()] = val
		else:
			arg_data[arg] = None
	return arg_data


def tag_list(env, page, args, tpl=''):
	'''Prints a list of objects within a given template'''
	if not tpl:
		return ''
	args = parse_list_args(args)
	data_list = quark.query_pages(env, page, args)
	render_list = []
	# renders the sub tpl block for each item
	for item in data_list:
		render_list.append(render_template(tpl, env, item))
	return '\n'.join(render_list)


def tag_include(env, page, filename):
	theme_dir = os.path.join(config.THEMES_DIR, page['theme'])
	if not filename.endswith('.tpl'):
		filename = '{0}.tpl'.format(filename)
	path = os.path.join(theme_dir, filename)
	if os.path.exists(path):
		include_tpl = quark.read_file(path)
		return render_template(include_tpl, env, page)
	else:
		print('Warning: Include file \'{0}\' doesn\'t exists.'.format(path))
		return ''


def tag_breadcrumbs(env, page, tpl):
	path = page['path']
	breadcrumbs = []
	while path:
		item_data = env['pages'].get(path)
		if not item_data:
			break
		breadcrumbs.insert(0, render_template(tpl, env, item_data))
		path, page = os.path.split(path)
	return '\n'.join(breadcrumbs)


def render_variable(env, page, var_name, args):
	# variable replacing, empty string if not found
	site_value = env.get(var_name, '')
	# if not found in env, try page
	tag_value = page.get(var_name, site_value)
	args = parse_variable_args(args)
	# render depends on the data type
	if isinstance(tag_value, datetime):
		return date_to_string(tag_value, args.get('fmt'))
	elif isinstance(tag_value, list):
		return ' '.join(tag_value)
	else:
		return tag_value


def render_template(tpl, env, page):
	'''Replaces the page variables in the given template'''
	# try to match the tag regular expressions by order
	for expr in tag_exprs:
		for match in re.finditer(expr, tpl, re.DOTALL):
			tag_match, tag_tokens = match.group(0), match.groups()
			# tag_name get the head, args takes the remaining groups
			tag_name, *args = tag_tokens
			cmd_name = "tag_" + tag_name
			if cmd_name in globals():
				tag_value = globals()[cmd_name](env, page, *args)
			else:
				tag_value = render_variable(env, page, tag_name, *args)
			tpl = tpl.replace(tag_match, tag_value)
	return tpl


def build_external_tags(filenames, permalink, tpl):
	tag_list = []
	for filename in filenames:
		url = quark.urljoin(permalink, filename)
		tag_list.append(tpl.format(url))
	return '\n'.join(tag_list)


def build_style_tags(filenames, permalink):
	tpl = '<link rel="stylesheet" type="text/css" href="{0}"/>'
	filenames = quark.extract_multivalues(filenames)
	filenames = [f for f in filenames if f.endswith('.css')]
	return build_external_tags(filenames, permalink, tpl)


def build_script_tags(filenames, permalink):
	tpl = '<script src="{0}"></script>'
	filenames = quark.extract_multivalues(filenames)
	filenames = [f for f in filenames if f.endswith('.js')]
	return build_external_tags(filenames, permalink, tpl)


def save_json(env, page):
	page = page.copy()
	page['date'] = date_to_string(page['date'])
	json_filepath = os.path.join(page['path'], 'index.json')
	quark.write_file(json_filepath, json.dumps(page))


def save_html(env, page):
	page = page.copy()
	# get css and javascript found in the folder
	page['styles'] = build_style_tags(page.get('styles', ''), page['permalink'])
	page['scripts'] = build_script_tags(page.get('scripts', ''), page['permalink'])
	# if a theme is not provided, uses default
	page_theme = page.get('theme', env['default_theme'])
	page['theme'] = page_theme
	page['page_theme_url'] = quark.urljoin(env['themes_url'], page_theme)
	# if not using custom template, it is defined by page type
	template_model = page.get('template', config.DEFAULT_TEMPLATE)
	html_templ = quark.read_html_template(page_theme, template_model)
	# replace template with page data and listings
	html = render_template(html_templ, env, page)
	path = page['path']
	quark.write_file(os.path.join(path, 'index.html'), html)
	if env['output_enabled']:
		print('"{0}" page generated.'.format(path or 'Home'))


def write_feed_file(env, filename):
	feed_dir = env.get('feed_dir', 'feed')
	feed_data = {
		'description': env.get('site_description'),
		'build_date': datetime.today()  # sets lastBuildDate
	}
	# create the feed directory
	if not os.path.exists(feed_dir):
		os.makedirs(feed_dir)
	feed_tpl = quark.read_file(config.MODEL_FEED_FILE)
	feed_data['link'] = quark.urljoin(env['base_url'], feed_dir, filename)
	feed_content = render_template(feed_tpl, env, feed_data)
	feed_path = os.path.join(feed_dir, filename)
	quark.write_file(feed_path, feed_content)
	if env['output_enabled']:
		print('Feed {!r} generated.'.format(feed_path))


def set_feed_source(env, pages):
	items_listed = int(env.get('feed_num', 8))  # default value
	pages = quark.dataset_sort(pages, 'date', 'desc')
	pages = quark.dataset_range(pages, items_listed)
	env['feeds'] = pages


def generate_feeds(env):
	sources = env.get('feed_sources')
	if not sources:
		print('No feeds generated.')
		return
	pages = env['pages'].values()
	# filtering the pages that shouldn't be listed in feeds
	pages = [p for p in pages if not 'nofeed' in p['props']]
	if 'all' in sources:
		set_feed_source(env, pages)
		write_feed_file(env, 'default.xml')
	if 'group' in sources:
		for group_name in env['groups']:
			pages = quark.dataset_filter_group(pages, group_name)
			set_feed_source(env, pages)
			write_feed_file(env, '{}.xml'.format(group_name))
