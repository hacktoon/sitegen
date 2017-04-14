# coding: utf-8

'''
===============================================================================
Infiniscribe - The Infinite Automaton Scriber of Nimus Ages

Author: Karlisson M. Bezerra
E-mail: contact@hacktoon.com
URL: https://github.com/hacktoon/infiniscribe
License: WTFPL - http://sam.zoy.org/wtfpl/COPYING
===============================================================================
'''

from . import parser
import sys

class Stamper:
	def __init__(self, text, include_path=''):
		self.include_path = include_path
		self.tree = parser.Parser(text, include_path=self.include_path).parse()

	def render(self, context):
		return self.tree.render(context)
