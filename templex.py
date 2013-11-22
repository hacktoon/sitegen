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

import re
import sys

from datetime import datetime

TOK_HTML = 'HTML'
TOK_COMMENT = 'Comment'
TOK_VARIABLE = 'Variable'
TOK_BLOCK = 'Block'

START_BLOCK = '{%'
END_BLOCK = '%}'
START_VAR = '{{'
END_VAR = '}}'
START_COMMENT = '{#'
END_COMMENT = '#}'

TAGS = (
	START_BLOCK,
	END_BLOCK,
	START_VAR,
	END_VAR,
	START_COMMENT,
	END_COMMENT
)

PATTERN = r'({0}.+?{1}|{2}.+?{3}|{4}.+?{5})'.format(*TAGS)
PARAMS_RE = re.compile('([a-zA-Z]+)\s*=\s*"(.+?)"')
COND_EXPR_RE = re.compile('([a-zA-Z]+)\s*=\s*"(.+?)"')
OP_RE = re.compile('(==|!=|)')

class Token():
	def __init__(self, value, token_type):
		self.value = value
		self.type = token_type
	
	def __str__(self):
		return '{!r} - {}'.format(self.type, self.value)


class Lexer():
	def __init__(self, template):
		regex = re.compile(PATTERN, re.DOTALL)
		self.fragments = regex.split(template)
		self.index = 0
	
	def clear_fragment(self, fragment):
		regex = re.compile(r'|'.join(TAGS))
		return re.sub(regex, '', fragment).strip()
	
	def is_block(self, fragment):
		start = fragment.startswith(START_BLOCK)
		end = fragment.endswith(END_BLOCK)
		return start and end
	
	def is_variable(self, fragment):
		start = fragment.startswith(START_VAR)
		end = fragment.endswith(END_VAR)
		return start and end
	
	def is_comment(self, fragment):
		start = fragment.startswith(START_COMMENT)
		end = fragment.endswith(END_COMMENT)
		return start and end
	
	def get_token(self):
		if self.index >= len(self.fragments):
			return
		raw_fragment = self.fragments[self.index]
		self.index += 1
		if self.is_block(raw_fragment):
			tok_type = TOK_BLOCK
		elif self.is_variable(raw_fragment):
			tok_type = TOK_VARIABLE
		elif self.is_comment(raw_fragment):
			tok_type = TOK_COMMENT
		else:
			return Token(raw_fragment, TOK_HTML)
		fragment = self.clear_fragment(raw_fragment)
		return Token(fragment, tok_type)


# PARSING CLASSES ======================================================

class Node():
	has_scope = False
	
	def __init__(self, params=''):
		self.children = []
		self.params = {}
		self.parse_params(params)
		self.process_params()
	
	def parse_params(self, params):
		if not params:
			return
		matches = re.findall(PARAMS_RE, params)
		if params and not matches:
			sys.exit('Encountered a malformed expression: {!r}'.format(params))
		self.params = {a:b for a,b in matches}

	def process_params(self):
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
	
	def __str__(self):
		pass


class ScopeNode(Node):
	has_scope = True


class Root(Node):
	def render(self, context):
		def render_child(child):
			return child.render(context)
		return ''.join(map(render_child, self.children))


class List(ScopeNode):
	def process_params(self):
		params = self.params
		if 'src' not in params.keys():
			sys.exit("Expected a collection to list.")
		self.source = params.get('src')
		self.order = params.get('ord')
		if self.order and self.order not in ['asc', 'desc']:
			sys.exit("Wrong ordering values.")
		self.limit = int(params.get('num', 0))

	def render(self, context):
		collection = self.lookup(self.source, context)
		if collection == self.source or not isinstance(collection, list):
			sys.exit("Trying to list a non-listable property.")
		
		if self.order and self.order == 'desc':
			collection.reverse()
		
		if self.limit:
			collection = collection[:self.limit]
		content = []
		for item in collection:
			iteration_content = []
			new_context = context.copy()
			new_context.update(item)
			for child in self.children:
				iteration_content.append(child.render(new_context))
			content.append(''.join(iteration_content))
		return ''.join(content).strip()

	def __str__(self):
		return 'list'


class Branch(ScopeNode):
	def __init__(self, args):
		super().__init__(args)
		self.alternative_branch = False
		self.consequent = []
		self.alternate = []

	def parse_params(self, expr):
		matches = re.findall(COND_EXPR_RE, expr)
		sys.exit(matches)
		if expr and not matches:
			sys.exit('Encountered a malformed expression: {!r}'.format(expr))
		self.params = {a:b for a,b in matches}
		
	def process_params(self):
		self.value = self.params.get('value')
		self.op = self.params.get('op')
		
	def process_condition(self, context):
		lvalue = self.lookup(lvar_name, context)
		rvalue = self.lookup(rvar_name, context)

	def set_alternative(self):
		self.alternative_branch = True
	
	def add_node(self, node):
		if self.alternative_branch:
			self.alternate.append(node)
		else:
			self.consequent.append(node)

	def render(self, context):
		if self.process_condition(context):
			children = self.consequent
		elif self.alternate:
			children = self.alternate
		else:
			return ''
		content = []
		for item in children:
			content.append(item.render(context))
		return ''.join(content)

	def __str__(self):
		return 'condition'


class Include(Node):
	def process_params(self):
		sys.exit('Wrong number of arguments.')
		self.tpl = ''

	def render(self, context):
		return self.tpl


class Variable(Node):
	def __init__(self, name, args):
		super().__init__(args)
		self.name = name

	def render(self, context):
		value = self.lookup(self.name, context)
		if isinstance(value, datetime) and 'fmt' in self.params:
			value = value.strftime(self.params['fmt'])
		return value


class HTML(Node):
	def parse_params(self, text):
		self.text = text

	def render(self, context):
		return self.text


class TemplateParser():
	def __init__(self, template):
		self.template = template
		self.include_path = None
	
	def set_include_path(self, path):
		self.include_path = path
	
	def parse(self):
		tree = Root()
		stack = [tree]
		lex = Lexer(self.template)

		token = lex.get_token()
		while token:
			node = None
			top_stack = stack[-1]
			
			if token.type == TOK_HTML:
				node = HTML(token.value)

			if token.type == TOK_VARIABLE:
				name, _, args = token.value.partition(' ')
				node = Variable(name, args)

			if token.type == TOK_BLOCK:
				command, _, args = token.value.partition(' ')
				if command == 'list':
					node = List(args)
				elif command == 'include':
					node = Include(self.include_path, args)
				elif command == 'if':
					node = Branch(args)
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
		if len(stack) > 1:
			# {!s} calls the str() method
			sys.exit('Non-closed block: "{!s}".'.format(stack[-1]))
		return tree
	
	def render(self, context):
		tree = self.parse()
		return tree.render(context)
