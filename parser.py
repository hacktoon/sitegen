# coding: utf-8

'''
==============================================================================
Template Language

Author: Karlisson M. Bezerra
E-mail: contact@hacktoon.com
URL: https://github.com/hacktoon/mnemonix
License: WTFPL - http://sam.zoy.org/wtfpl/COPYING

==============================================================================
'''

import re
import sys

from lexer import *
from scanner import *

VAR_TOKEN = 'variable'
OPEN_BLOCK_TOKEN = 'open_block'
CLOSE_BLOCK_TOKEN = 'close_block'
TEXT_TOKEN = 'text'


class Node():
	has_scope = False
	
	def __init__(self, token=None):
		self.children = []
		self.parse_token(token)
	
	def get_params(self, token):
		cmd, expr = map(lambda x: x.strip(), token.value.split(' ', 1))
		return cmd, expr
	
	def parse_token(self, token):
		pass

	def add_node(self, node):
		self.children.append(node)

	def render(self, context):
		pass


class ScopeNode(Node):
	has_scope = True


class Root(Node):
	def render(self, context):
		def render_child(child):
			return child.render(context)
		return ''.join(map(render_child, self.children))


class Attribution(Node):
	def parse_token(self, token):
		command, expr = self.get_params(token)
		var, value = expr.split('=', 1)
		self.var_name = var.strip()
		self.value = value.strip()

	def render(self, context):
		context[self.var_name] = self.value
		return ''


class List(ScopeNode):
	def parse_token(self, token):
		command, expr = self.get_params(token)
		self.source = expr.strip()

	def render(self, context):
		if self.source not in context:
			sys.exit("Trying to list a non-existent property.")
		if not isinstance(context[self.source], list):
			sys.exit("Trying to list a non-listable property.")
		
		collection = context[self.source]
		content = []
		for item in collection:
			iteration_content = []
			new_context = context.copy()
			new_context.update(item)
			for child in self.children:
				iteration_content.append(child.render(new_context))
			content.append(''.join(iteration_content))
		return ''.join(content).strip()


class Branch(ScopeNode):
	def parse_token(self, token):
		command, self.expr = self.get_params(token)
		self.has_alternative = False
		self.consequent = []
		self.alternate = []

	def set_alternative(self):
		self.has_alternative = True
	
	def add_node(self, node):
		if self.has_alternative:
			self.alternate.append(node)
		else:
			self.consequent.append(node)

	def render(self, context):
		condition = True
		if condition:
			children = self.consequent
		elif self.alternate:
			children = self.alternate
		else:
			return ''
		content = []
		for item in children:
			content.append(item.render(context))
		return ''.join(content)


class Breadcrumb(ScopeNode):
	def parse_token(self, token):
		self.text = token.value

	def render(self, context):
		return self.text


class Include(Node):
	def parse_token(self, token):
		command, tpl = self.get_params(token)
		self.tpl = tpl.strip()

	def render(self, context):
		return self.text


class Variable(Node):
	def parse_token(self, token):
		self.name = token.value

	def render(self, context):
		if self.name in context:
			return context[self.name]
		else:
			return ''


class Text(Node):
	def parse_token(self, token):
		self.text = token.value

	def render(self, context):
		return self.text


template = open('template').read()

env = {
	'site_title': 'Home page',
	'title': 'Home teste',
	'pages': [{'title': 'pagina 1'}, {'title': 'pagina 2'}, {'title': 'pagina 3'}]
}


def render(template, context):
	root = Root()
	stack = [root]

	for fragment in []:
		if not fragment: # ignore whitespaces
			continue
		token = Token(fragment)
		node = None
		
		if token.type == TEXT_TOKEN:
			node = Text(token)
		
		if token.type == VAR_TOKEN:
			node = Variable(token)

		if token.type == OPEN_BLOCK_TOKEN:
			command = token.value.split()[0]
			if command == 'set':
				node = Attribution(token)
			elif command == 'list':
				node = List(token)
			elif command == 'if':
				node = Branch(token)
			elif command == 'else':
				node = stack[-1]
				if isinstance(node, Branch):
					node.set_alternative()
				continue
			elif command == 'include':
				node = Include(token)
			elif command == 'breadcrumbs':
				node = Breadcrumb(token)
			else:
				sys.exit('Command not recognized.')

		if token.type == CLOSE_BLOCK_TOKEN:
			if len(stack) == 1:
				sys.exit('Unexpected end tag!')
			if stack[-1].has_scope:
				stack.pop()

		if node:
			stack[-1].add_node(node);
			if node.has_scope:
				stack.append(node)
		
	return root.render(context)

print(render(template, env))
