from . import parser
import sys

class Stamper:
	def __init__(self, template, filename='', include_path=''):
		self.template = template
		self.filename = filename
		self.include_path = include_path

	def render(self, context):
		parse_tree = parser.Parser(self.template, 
			filename=self.filename, include_path=self.include_path).parse()
		return parse_tree.render(context)