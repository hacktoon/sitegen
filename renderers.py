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

import json

import templex
from errors import *

class ContentRenderer():
	def __init__(self, template):
		self.template = self.read_template(template)

	def read_template(self, tpl_filename):
		'''Returns a template string from the template folder'''
		if not tpl_filename.endswith('.tpl'):
			tpl_filename = '{0}.tpl'.format(tpl_filename)
		tpl_filepath = path_join(TEMPLATES_DIR, tpl_filename)
		if not os.path.exists(tpl_filepath):
			raise FileNotFoundError()
		return read_file(tpl_filepath)

	def render(self):
		pass


class JSONRenderer(ContentRenderer):
	def __init__(self):
		self.date_format = '%Y-%m-%d %H:%M:%S'

	def render(self, page):
		page_dict = page.serialize()
		page_dict['date'] = page_dict['date'].strftime(self.date_format)
		return json.dumps(page_dict)


class RSSRenderer(ContentRenderer):
	def render(self, page_dict):
		pass


class HTMLRenderer(ContentRenderer):
	def __init__(self):
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

	def render(self, page):
		page_dict = page.serialize()
		page_dict['styles'] = self.build_style_tags(page._styles)
		page_dict['scripts'] = self.build_script_tags(page._scripts)
		
		return ''
		#renderer = TemplateParser(self.template)
		#return renderer.render(page_dict)
