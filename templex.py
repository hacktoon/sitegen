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
import os
import sys
from datetime import datetime

import book_dweller
from alarum import TemplateError

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

TOKEN_RE = r'({0}.+?{1}|{2}.+?{3}|{4}.+?{5})'.format(*TAGS)
PARAMS_RE = re.compile('([a-zA-Z_-]+)\s*=\s*"(.*?)"')

class Token():
	def __init__(self, value, token_type):
		self.value = value
		self.type = token_type
	
	def __str__(self):
		return '{!r} - {}'.format(self.type, self.value)


class Lexer():
	def __init__(self, template):
		regex = re.compile(TOKEN_RE, re.DOTALL)
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
			raise TemplateError('Encountered a malformed expression: {!r}'.format(params))
		self.params = {a:b for a,b in matches}

	def process_params(self):
		pass

	def add_node(self, node):
		self.children.append(node)

	def lookup(self, name, context):
		keys = name.split('.')
		if keys[0] not in context:
			return None
		if len(keys) <= 1:
			return context.get(keys[0])
		reference = context[keys[0]]
		for k in keys[1:]:
			if not k in reference.keys():
				return None
			reference = reference.get(k)
		return reference

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


class PageList(ScopeNode):
	def process_params(self):
		params = self.params
		self.order = params.get('ord')
		self.group = params.get('group')
		if self.order and self.order not in ['asc', 'desc']:
			raise TemplateError('Wrong ordering values for the "ord" parameter.')
		try:
			self.number = abs(int(params.get('num', 0)))
		except ValueError:
			raise TemplateError('The "num" parameter must be an integer.')
	
	def filter_group(self, pages):
		if self.group:
			return [p for p in pages if p.group == self.group]
		return pages
	
	def filter_number(self, pages):
		if self.number:
			pages = pages[:self.number]
		return pages
			
	def set_order(self, pages):
		if self.order and self.order == 'desc':
			pages.reverse()
	
	def render(self, context):
		pages = self.lookup('pages', context)
		if not pages:
			raise TemplateError('Trying to list a non-listable property')

		pages = self.filter_group(pages)
		self.set_order(pages)
		pages = self.filter_number(pages)

		content = []
		for page in pages:
			if not page.is_listable():
				continue
			iteration_content = []
			context['each'] = page
			for child in self.children:
				iteration_content.append(child.render(context))
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
		
	def process_params(self):
		self.var = self.params.get('var')
		if not self.var:
			raise TemplateError('Need a value to compare')
		self.equal = self.params.get('equal')
		self.diff = self.params.get('diff')
		if self.equal and self.diff:
			raise TemplateError('Too much conditional clauses')

	def process_condition(self, context):
		var = self.lookup(self.var, context)
		if not self.equal and not self.diff:
			return bool(var)
		if self.equal:
			return var == self.equal
		if self.diff:
			return var != self.diff

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
	def __init__(self, include_path, args):
		if not include_path:
			raise TemplateError('Include file not specified.')
		self.include_path = include_path
		super().__init__(args)

	def process_params(self):
		filename = self.params.get('file')
		if not filename.endswith('.tpl'):
			filename = '{0}.tpl'.format(filename)
		path = os.path.join(self.include_path, filename)
		tpl = book_dweller.bring_file(path)
		self.parser = TemplateParser(tpl)

	def render(self, context):
		return self.parser.render(context)


class Parse(Node):
	def __init__(self, include_path, args):
		if not include_path:
			raise TemplateError('Include file not specified.')
		self.include_path = include_path
		super().__init__(args)

	def process_params(self):
		filename = self.params.get('file')
		if not filename.endswith('.tpl'):
			filename = '{0}.tpl'.format(filename)
		path = os.path.join(self.include_path, filename)
		self.text = book_dweller.read_file(path)

	def render(self, context):
		return self.text


class Variable(Node):
	def __init__(self, name, args):
		super().__init__(args)
		self.name = name

	def render(self, context):
		value = self.lookup(self.name, context)
		if not value:
			return ''
		if isinstance(value, datetime): 
			if 'fmt' in self.params:
				value = value.strftime(self.params['fmt'])
			else:
				value = value.strftime('%Y-%m-%d %H:%M:%S')
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
	
	def handle_token(self, token, stack):
		node = None
		top_stack = stack[-1]
		
		if token.type == TOK_HTML:
			node = HTML(token.value)

		if token.type == TOK_VARIABLE:
			name, _, args = token.value.partition(' ')
			node = Variable(name, args)

		if token.type == TOK_BLOCK:
			command, _, args = token.value.partition(' ')
			if command == 'pagelist':
				node = PageList(args)
			elif command == 'include':
				node = Include(self.include_path, args)
			elif command == 'parse':
				node = Parse(self.include_path, args)
			elif command == 'if':
				node = Branch(args)
			elif command == 'else':
				if not isinstance(top_stack, Branch):
					raise TemplateError('Unexpected "else" tag.')
				top_stack.set_alternative()
			elif command == 'end':
				if len(stack) == 1:
					raise TemplateError('Unmatched closing block.')
				stack.pop()
			else:
				raise TemplateError('{!r} command not recognized!'.format(command))
		if node:
			top_stack.add_node(node)
			if node.has_scope:
				stack.append(node)
		return node

	def parse(self):
		tree = Root()
		stack = [tree]
		lex = Lexer(self.template)

		token = lex.get_token()
		while token:
			self.handle_token(token, stack)
			token = lex.get_token()
		if len(stack) > 1:
			raise TemplateError('Non-closed block: "{!s}".'.format(stack[-1]))
		return tree
	
	def render(self, context):
		tree = self.parse()
		return tree.render(context)
