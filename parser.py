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

import sys
import re
from lexer import *

class ParserException(Exception):
	pass

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

	def lookup(self, name, context):
		if '.' in name:
			key, prop = name.split('.', 1)
		else:
			key, prop = name, ''
		try:
			if prop:
				return context[key][prop]
			else:
				return context[key]
		except KeyError:
			return name

	def render(self, context):
		pass


class ScopeNode(Node):
	has_scope = True


class Root(Node):
	def render(self, context):
		def render_child(child):
			return child.render(context)
		return ''.join(map(render_child, self.children))


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
	def process_condition(self, args):
		pass
	
	def parse_token(self, args):
		self.args = args
		self.alternative_branch = False
		self.consequent = []
		self.alternate = []

	def set_alternative(self):
		self.alternative_branch = True
	
	def add_node(self, node):
		if self.alternative_branch:
			self.alternate.append(node)
		else:
			self.consequent.append(node)

	def render(self, context):
		if self.process_condition(self.args, context):
			children = self.consequent
		elif self.alternate:
			children = self.alternate
		else:
			return ''
		content = []
		for item in children:
			content.append(item.render(context))
		return ''.join(content)


class EqualBranch(Branch):
	def process_condition(self, args, context):
		if len(args) != 2:
			sys.exit("Comparison mal-formed.")
		lvar_name, rvar_name = args
		lvalue = self.lookup(lvar_name, context)
		rvalue = self.lookup(rvar_name, context)
		return lvalue == rvalue


class DifferentBranch(Branch):
	def process_condition(self, args, context):
		if len(args) != 2:
			sys.exit("Comparison mal-formed.")
		lvar_name, rvar_name = args
		lvalue = self.lookup(lvar_name, context)
		rvalue = self.lookup(rvar_name, context)
		return lvalue != rvalue


class DefinedBranch(Branch):
	def process_condition(self, args, context):
		if len(args) != 1:
			sys.exit("Comparison mal-formed.")
		return args[0] != self.lookup(args[0], context)


class UndefinedBranch(Branch):
	def process_condition(self, args, context):
		if len(args) != 1:
			sys.exit("Comparison mal-formed.")
		return args[0] == self.lookup(args[0], context)


class Include(Node):
	def parse_token(self, args):
		if len(args) > 1:
			sys.exit('Wrong number of arguments.')
		self.tpl = args

	def render(self, context):
		return self.text


class Attribution(Node):
	def parse_token(self, args):
		if not args:
			sys.exit("Expected arguments in 'set' command!")
		self.name, self.value = args
		
	def render(self, context):
		context[self.name] = self.value
		return ''


class Variable(Node):
	def parse_token(self, value):
		self.value = value

	def render(self, context):
		return self.lookup(self.value, context)


class HTML(Node):
	def parse_token(self, text):
		self.text = text

	def render(self, context):
		return self.text


def parse(template):
	tree = Root()
	stack = [tree]
	lex = Lexer(template)

	token = lex.get_token()
	while token:
		node = None
		top_stack = stack[-1]

		if token.type == TOK_HTML:
			node = HTML(token.value)

		if token.type == TOK_VARIABLE:
			node = Variable(token.value)

		if token.type == TOK_BLOCK:
			expr = re.split(r'\s+', token.value)
			command, args = expr[0], []
			if len(expr) > 1:
				args = expr[1:]

			if command == 'set':
				node = Attribution(args)
			elif command == 'list':
				node = List(args)
			elif command == 'include':
				node = Include(args)
			elif command == 'if:equal':
				node = EqualBranch(args)
			elif command == 'if:different':
				node = DifferentBranch(args)
			elif command == 'if:defined':
				node = DefinedBranch(args)
			elif command == 'if:undefined':
				node = UndefinedBranch(args)
			elif command == 'else':
				if not isinstance(top_stack, Branch):
					sys.exit("Unexpected 'else' tag.")
				top_stack.set_alternative()
			elif command == 'end':
				if len(stack) == 1:
					sys.exit("Unmatched closing block.")
				stack.pop()
			else:
				sys.exit("{!r} command not recognized!".format(command))
		if node:
			top_stack.add_node(node)
			if node.has_scope:
				stack.append(node)
		token = lex.get_token()
	return tree

env = {
	'title': 'Home teste',
	'site': {'title': 'Hacktoon!'},
	'pages': [{'title': 'pagina 1'}, {'title': 'pagina 2'}, {'title': 'pagina 3'}]
}

template = open('template').read()

print(parse(template).render(env))
