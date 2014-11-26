# -*- encoding: UTF-8 -*-

import sys
from alarum import PageValueError

TOK_NAME = 'name'
TOK_TEXT = 'content'
TOK_EOF = '\0'
TOK_ASSIGN = '='
TOK_COMMA = ','
TOK_NEWLINE = '\n'
TOK_OPENLIST = '['
TOK_CLOSELIST = ']'
TOK_OPENGROUP = '{'
TOK_CLOSEGROUP = '}'

KEYCHARS = ''.join([
	TOK_ASSIGN,
	TOK_COMMA,
	TOK_NEWLINE,
	TOK_OPENLIST,
	TOK_CLOSELIST,
	TOK_OPENGROUP,
	TOK_CLOSEGROUP
])

class Token:
	def __init__(self, type, value):
		self.type = type
		self.value = value
		self.line = 1
		self.column = 0

	def __str__(self):
		type = 'NAME' if self.type == TOK_NAME else 'SYMBOL'
		return "({!r}: {!r})".format(type, self.value)

	def __repr__(self):
		val = self.value
		return '{!r}'.format(val if val != TOK_NEWLINE else '\n')


class MemReader:
	def __init__(self, text):
		self.index = 0
		self.text = text
		self.line = 1
		self.column = 0
		self.tokens = []
		self.current_token = None
		self.data = {}
		self.stack = [self.data]

	def error(self, msg):
		raise PageValueError('{} at line {}, column {}'.format(
			msg, self.line, self.column))

	def create_token(self, type, value):
		if not value:
			return
		token = Token(type, value)
		token.line = self.line
		token.column = self.column
		self.tokens.append(token)

	def tokenize(self):
		text = self.text.strip()
		cache = []
		for char in text:
			self.column += 1
			if char in KEYCHARS:
				if char == TOK_NEWLINE:
					self.line += 1
					self.column = 0
				name = ''.join(cache).strip()
				self.create_token(TOK_NAME, name)
				self.create_token(char, char)
				cache = []
			elif char not in KEYCHARS:
				cache.append(char)
			else:
				self.error('Wrong character: '+ char)
		# remaining chars
		name = ''.join(cache).strip()
		self.create_token(TOK_NAME, name)
		self.current_token = self.tokens[0]

	def next_token(self):
		self.index += 1
		try:
			next = self.tokens[self.index]
		except IndexError:
			next = Token(TOK_EOF, TOK_EOF)
		self.current_token = next
		return next

	def skip_newlines(self):
		while self.current_token.type == TOK_NEWLINE:
			self.next_token()

	def consume(self, expected):
		token = self.current_token
		if token.type == TOK_EOF:
			return
		if token.type != expected:
			self.error('Expected a {!r}'.format(expected))
		self.next_token()

	def parse_group(self):
		rules = {}
		self.stack.append(rules)
		self.skip_newlines()
		while self.current_token.type not in (TOK_CLOSEGROUP, TOK_EOF):
			self.parse_rule()
			self.skip_newlines()
		self.consume(TOK_CLOSEGROUP)
		self.stack.pop()
		return rules

	def parse_list(self):
		names = []
		self.skip_newlines()
		while True:
			token = self.current_token
			if token.type == TOK_CLOSELIST:
				self.next_token()
				break
			if token.type == TOK_NAME:
				names.append(token.value)
				self.next_token()
				self.skip_newlines()
			else:
				self.error('Expected a name, got {!r}'.format(token.value))
			token = self.current_token
			if token.type == TOK_COMMA:
				token = self.next_token()
				self.skip_newlines()
				continue
			elif token.type == TOK_CLOSELIST:
				self.next_token()
				break
			else:
				self.error('Invalid syntax')
		return names

	def parse_value(self):
		token = self.current_token
		if token.type == TOK_NAME:
			value = token.value
			self.next_token()
		elif token.type == TOK_OPENLIST:
			self.next_token()
			value = self.parse_list()
		elif token.type == TOK_OPENGROUP:
			self.next_token()
			value = self.parse_group()
		else:
			self.error('Invalid value format')
		return value

	def parse_text(self):
		if len(self.stack) > 1:
				self.error('Forbidden key name')
		self.next_token()
		self.skip_newlines()
		text = self.tokens[self.index:]
		self.index = len(self.tokens) - 1
		self.next_token()
		return ''.join(map(lambda x: x.value, text))

	def parse_rule(self):
		token = self.current_token
		if token.type != TOK_NAME:
			self.error('Expected a name, got {!r}'.format(token.value))
		name = token.value
		if name == TOK_TEXT:
			text = self.parse_text()
			self.data[name] = text
			return
		token = self.next_token()
		self.skip_newlines()
		if token.type == TOK_ASSIGN:
			self.next_token()
			if self.current_token.type == TOK_NEWLINE:
				value = ''
				self.skip_newlines()
			else:
				self.skip_newlines()
				value = self.parse_value()
				self.consume(TOK_NEWLINE)
		elif token.type in (TOK_NEWLINE, TOK_EOF):
			value = True
			self.next_token()
		else:
			self.error('Invalid syntax')
		self.stack[-1][name] = value

	def parse_ruleset(self):
		while self.current_token.type not in (TOK_EOF, TOK_CLOSEGROUP):
			self.parse_rule()
			self.skip_newlines()

	def parse(self):
		self.tokenize()
		self.parse_ruleset()
		return self.data