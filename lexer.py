import string
import sys

EOL = '\n'
EOT = '\0'
CMD_START = '#'
WHITESPACE = ' \n\t\r'
KEYWORDS = 'if else elseif childlist pagelist end put parse include null'.split()
SYMBOLS = '!=,()"'
STRING_DELIMITER = '"'
IDENTIFIERS = string.ascii_letters + '._'
DIGITS = string.digits

TOK_HTML = 'HTML'
TOK_ID = 'Identifier'
TOK_KEYWORD = 'Keyword'
TOK_NUMBER = 'Number'
TOK_STRING = 'String'
TOK_OPEN_PAREN = '('
TOK_CLOSE_PAREN = ')'
TOK_EQUALS = '=='
TOK_NOTEQUALS = '!='
TOK_COMMA = ','
TOK_ATTRIB = '='


def is_digit(c):
	return c in DIGITS

def is_keyword(c):
	return c in KEYWORDS

def is_whitespace(c):
	return c in WHITESPACE

def is_identifier(c):
	return c in IDENTIFIERS


class Char():
	def __init__(self, line, col, value):
		self.line = line
		self.column = column
		self.value = value
	
	def __str__(self):
		args = self.line, self.column, self.value
		return "Line {}, column {} - \t{!r}".format(*args)


class Token():
	def __init__(self, value, token_type):
		self.value = value
		self.type = token_type
		self.line = 0
		self.column = 0

	def __str__(self):
		return '{!r} - {}'.format(self.type, self.value)


class Scanner():
	def __init__(self, template):
		self.template = template
		self.index = 0
		self.line = 1
		self.column = 1
	
	def get_char(self):
		if self.index >= len(self.template):
			return Char(self.line, self.column, EOT)
		c = self.template[self.index]
		if c == EOL:
			self.line += 1
			self.column = 1
		else:
			self.column += 1
		char = Char(self.line, self.column, c)
		self.index += 1
		return char


class Lexer():
	def __init__(self, template):
		self.template = template
		self.scanner = Scanner(template)
		self.in_block = False
		self.token_buffer = None

	def get_token(self):
		cbuffer = None
		
		if self.token_buffer:
			token = self.token_buffer
			self.token_buffer = None
			yield token
		
		html = []
		cbuffer = []
		scanner = self.scanner
		c = scanner.get_char()
		while True:
			if c.value == EOT:
				if self.in_block:
					raise TemplateError('Tag not closed!')
				elif html:
					# remaining html chars
					yield Token(''.join(html), TOK_HTML)
			if self.in_block:  # lexing of actual language elements
				# whitespace
				if is_whitespace(c.value):
					c = scanner.get_char()
				
				# identifiers
				elif is_identifier(c.value):
					identifier = c.value
					c = scanner.get_char()
					while is_identifier(c.value):
						identifier += c.value
						c = scanner.get_char()
					if is_command(identifier):
						yield Token(identifier, TOK_COMMAND)
					else:
						yield Token(identifier, TOK_ID)
				else:
					raise TemplateError('Not a valid character: {!r}'.format(c.value))
			elif c.value == CMD_START:
				# command started, check if there´s a real command
				while is_identifier(c.value):
					cbuffer.append(c.value)
					c = scanner.get_char()
				# possible command formed, check if next char is parenthesis
				if is_keyword(''.join(cbuffer)) and c.value == OPEN_ARG:
					self.token_buffer = Token(''.join(cbuffer), TOK_COMMAND)
					self.in_block = True
				else:
					self.command_start = False
					html += cbuffer
				content = ''.join(html)
				cbuffer = []
				html = []
				yield Token(content, TOK_HTML)
			else:
				if c.value == '#':
					self.command_start = True
				else:
					html.append(c.value)
			c = scanner.get_char()


template = '''<html> #pagelist(num=5, ord="desc", group="news")
	<li> #put(varname) </li> 
	#end </html>'''
lex = Lexer(template)
for x in lex.get_token():
	print(x)
