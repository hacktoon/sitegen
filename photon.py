# coding: utf-8

'''
==============================================================================
Ion - A shocking simple static (site) generator

Author: Karlisson M. Bezerra
E-mail: contact@hacktoon.com
URL: https://github.com/karlisson/ion
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


def tag_list(env, page, args, tpl):
	'''Prints a list of objects within a given template'''
	args = parse_list_args(args)
	data_list = quark.query(env, page, args)
	render_list = []
	# renders the sub tpl block for each item
	for item in data_list:
		render_list.append(render_template(tpl, env, item))
	return '\n'.join(render_list)


def tag_include(env, page, filename):
	theme_dir = quark.get_page_theme_dir(page['theme'])
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
		item_data = env['pages'][path]
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


def render_template(tpl, env, page, tpl_name=None):
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
		filename = filename.strip()
		url = os.path.join(permalink, filename)
		tag_list.append(tpl.format(url))
	return '\n'.join(tag_list)


def build_style_tags(filenames, permalink):
	tpl = '<link rel="stylesheet" type="text/css" href="{0}"/>'
	filenames = [f for f in filenames.split(',') if f.endswith('.css')]
	return build_external_tags(filenames, permalink, tpl)


def build_script_tags(filenames, permalink):
	tpl = '<script src="{0}"></script>'
	filenames = [f for f in filenames.split(',') if f.endswith('.js')]
	return build_external_tags(filenames, permalink, tpl)


def save_json(env, page):
	page = page.copy()
	page['date'] = date_to_string(page['date'])
	json_filepath = os.path.join(page['path'], 'index.json')
	page['children'] = None
	quark.write_file(json_filepath, json.dumps(page))


def save_html(env, page):
	page = page.copy()
	# get css and javascript found in the folder
	page['css'] = build_style_tags(page.get('css', ''), page['permalink'])
	page['js'] = build_script_tags(page.get('js', ''), page['permalink'])
	page['page_theme_url'] = quark.urljoin(env['themes_url'], page['theme'])
	# if not using custom theme, use default
	template_model = page.get('template', config.THEMES_DEFAULT_TEMPL)
	html_templ = quark.read_html_template(page['theme'], template_model)
	# replace template with page data and listings
	html = render_template(html_templ, env, page)
	path = page['path']
	quark.write_file(os.path.join(path, 'index.html'), html)
	if not path:
		path = 'Home'
	print('"{0}" page generated.'.format(path))


def save_rss(env):
	rss_data = {
		'link': env['base_url'],
		'description': env.get('site_description'),
		# get lastBuildDate
		'build_date': datetime.today()
	}
	rss_tpl = quark.read_rss_template()
	# populate RSS items with the page index
	rss_doc = render_template(rss_tpl, env, rss_data)
	quark.write_file(config.FEED_URL, rss_doc)
	print('Feed "{}" generated.'.format(config.FEED_URL))
