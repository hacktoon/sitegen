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
	
	def __init__(self, args=None):
		self.children = []
		self.parse_args(args)
	
	def parse_args(self, args):
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
	def parse_args(self, args):
		if not args:
			sys.exit("Expected a collection to list.")
		self.source = args[0]
		if len(args) == 2:
			try:
				self.limit = int(args[1])
			except ValueError:
				sys.exit("Expected a number in list command.")
		elif len(args) > 2:
			sys.exit("Wrong number of arguments. Expected 2.")
		else:
			self.limit = None

	def render(self, context):
		collection = self.lookup(self.source, context)
		if collection == self.source:
			sys.exit("Trying to list a non-existent property.")
		if not isinstance(collection, list):
			sys.exit("Trying to list a non-listable property.")
		
		if self.limit:
			if self.limit > 0:
				# return the last x, as [1,2,3,4,5,6][-2:] => [5,6]
				collection = collection[-self.limit:]
			else:
				# return the first x
				collection = collection[:-self.limit]
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
	def process_condition(self, args):
		pass
	
	def parse_args(self, args):
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

	def __str__(self):
		return 'if'


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
	def parse_args(self, args):
		if len(args) != 1:
			sys.exit('Wrong number of arguments.')
		self.tpl = args[0]

	def render(self, context):
		return self.tpl


class Attribution(Node):
	def parse_args(self, args):
		if not args:
			sys.exit("Expected arguments in 'set' command!")
		if len(args) != 2:
			sys.exit("Wrong number of arguments in 'set' command!")
		self.name, self.value = args
		
	def render(self, context):
		context[self.name] = self.value
		return ''


class Variable(Node):
	def parse_args(self, value):
		self.value = value

	def render(self, context):
		return self.lookup(self.value, context)


class HTML(Node):
	def parse_args(self, text):
		self.text = text

	def render(self, context):
		return self.text


class Template():
	def __init__(self, template):
		self.template = template

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
		if len(stack) > 1:
			# {!s} calls the str() method
			sys.exit('Non-closed block: "{!s}".'.format(stack[-1]))
		return tree
	
	def render(self, context):
		tree = self.parse()
		return tree.render(context)
