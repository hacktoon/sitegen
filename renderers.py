

import json

import templex
from exceptions import *

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
		
		return ''
		#renderer = TemplateParser(self.template)
		#return renderer.render(page_dict)
