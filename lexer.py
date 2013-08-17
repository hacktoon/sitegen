import string
import sys

EOL = '\n'
EOT = '\0'

TOK_HTML = 'HTML'
TOK_ID = 'Identifier'
TOK_COMMAND = 'Keyword'

WHITESPACE = ' \n\t\r'
COMMANDS = 'ifdef ifndef equals list end print set include'.split()
IDENTIFIERS = string.ascii_letters

def is_command(c):
	return c in COMMANDS

def is_whitespace(c):
	return c in WHITESPACE

def is_identifier(c):
	return c in IDENTIFIERS

class Char():
	def __init__(self, line, col, index, value):
		self.line = line
		self.col = col
		self.value = value
		self.index = index
	
	def __str__(self):
		args = self.line, self.col, self.value
		return "Line {}, column {} - {!r}".format(*args)


class Scanner():
	def __init__(self, template):
		self.template = template
		self.index = 0
		self.line = 1
		self.column = 1
	
	def get_char(self):
		if self.index >= len(self.template):
			return Char(self.line, self.column, self.index, EOT)
		c = self.template[self.index]
		if c == EOL:
			self.line += 1
			self.column = 1
		else:
			self.column += 1
		char = Char(self.line, self.column, self.index, c)
		self.index += 1
		return char


class Token():
	def __init__(self, value, token_type):
		self.value = value
		self.type = token_type
	
	def __str__(self):
		return '{!r} - {}'.format(self.type, self.value)


class Lexer():
	def __init__(self, template):
		self.template = template
		self.scanner = Scanner(template)
		self.in_block = False
		self.command_start = False

	def get_token(self):
		scanner = self.scanner
		html = []
		buffer = []
		c = scanner.get_char()
		while True:
			if c.value == EOT:
				if self.in_block:
					sys.exit('Tag not closed!')
				elif html:
					# remaining chars
					return Token(''.join(html), TOK_HTML)
				else:
					return Token('', EOT)
			if self.command_start:  # lexing of actual language elements
				# whitespace
				elif is_whitespace(c.value):
					c = scanner.get_char()
				
				# identifiers
				elif is_identifier(c.value):
					identifier = c.value
					c = scanner.get_char()
					while is_identifier(c.value):
						identifier += c.value
						c = scanner.get_char()
					if is_keyword(identifier):
						return Token(identifier, TOK_KEYWORD)
					else:
						return Token(identifier, TOK_ID)
				else:
					sys.exit('Not a valid character: {!r}'.format(c.value))
			else:
				if val == '#':
					self.command_start = True
					buffer.append(c.value)
					#return Token(''.join(html), TOK_HTML)
				else:
					html.append(c.value)
				c = scanner.get_char()
