# -*- encoding: UTF-8 -*-

import sys
from alarum import PageValueError

NEWLINE = '\n'

TOK_NAME = 'name'
TOK_TEXT = 'content'
TOK_EOF = '\0'
TOK_ASSIGN = '='
TOK_COMMA = ','
TOK_OPENLIST = '['
TOK_CLOSELIST = ']'
TOK_OPENGROUP = '{'
TOK_CLOSEGROUP = '}'

KEYCHARS = ''.join([
	NEWLINE,
	TOK_ASSIGN,
	TOK_COMMA,
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
		return "({!r}: {!r})".format(self.type, self.value)

	def __repr__(self):
		return '{!r}'.format(self.value)


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
		token = self.current_token
		raise PageValueError('{} at line {}, column {}'.format(
			msg, token.line, token.column))

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
		inlist = False
		for index, char in enumerate(text):
			if char not in KEYCHARS or not inlist and char == TOK_COMMA:
				cache.append(char)
				continue
			name = ''.join(cache).strip()
			inlist = {
				TOK_OPENLIST: True,
				TOK_CLOSELIST: False
			}.get(char, inlist)
			if name == TOK_TEXT:
				self.create_token(TOK_TEXT, text[index:].strip())
				return
			self.create_token(TOK_NAME, name)
			if char == NEWLINE:
				self.line += 1
				self.column = 0
			else:
				self.column += 1
				self.create_token(char, char)
			cache = []
				
		# remaining chars
		name = ''.join(cache).strip()
		self.create_token(TOK_NAME, name)

	def next_token(self):
		self.index += 1
		try:
			next = self.tokens[self.index]
		except IndexError:
			next = Token(TOK_EOF, TOK_EOF)
		self.current_token = next
		return next

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
		while self.current_token.type not in (TOK_CLOSEGROUP, TOK_EOF):
			self.parse_rule()
		self.consume(TOK_CLOSEGROUP)
		self.stack.pop()
		return rules

	def parse_list(self):
		names = []
		while True:
			token = self.current_token
			if token.type == TOK_CLOSELIST:
				self.next_token()
				break
			if token.type == TOK_NAME:
				names.append(token.value)
				self.next_token()
			else:
				self.error('Expected a name, got {!r}'.format(token.value))
			token = self.current_token
			if token.type == TOK_COMMA:
				token = self.next_token()
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

	def parse_rule(self):
		token = self.current_token
		if token.type not in (TOK_NAME, TOK_TEXT):
			self.error('Expected a name, got {!r}'.format(token.value))
		name = token.value
		if token.type == TOK_TEXT:
			if len(self.stack) > 1:
				self.error('Wrong syntax')
			self.data[TOK_TEXT] = token.value
			self.next_token()
			return
		token = self.next_token()
		if token.type == TOK_ASSIGN:
			self.next_token()
			value = self.parse_value()
		else:
			self.error('Invalid syntax')
		self.stack[-1][name] = value

	def parse_ruleset(self):
		while self.current_token.type not in (TOK_EOF, TOK_CLOSEGROUP):
			self.parse_rule()

	def parse(self):
		self.tokenize()
		self.current_token = self.tokens[0]
		self.parse_ruleset()
		return self.data