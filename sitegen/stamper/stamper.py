# coding: utf-8

'''
===============================================================================
Sitegen

Author: Karlisson M. Bezerra
E-mail: contact@hacktoon.com
URL: https://github.com/hacktoon/sitegen
License: WTFPL - http://sam.zoy.org/wtfpl/COPYING
===============================================================================
'''

from . import parser


class Stamper:
	def __init__(self, text, include_path=''):
		self.include_path = include_path
		self.tree = parser.Parser(text, include_path=include_path).parse()

	def render(self, context) -> str:
		return self.tree.render(context)
