import string
import sys

EOL = '\n'
EOT = '\0'

TOK_HTML = 'HTML'
TOK_ID = 'Identifier'
TOK_DIGIT = 'Digit'
TOK_KEYWORD = 'Keyword'
TOK_SYMBOL = 'Symbol'

WHITESPACE = [' ', '\t', '\n', '\r']
KEYWORDS = 'if else endif loop endloop say partial set include and not or'.split()
SYMBOLS = '+-*/^%()<>=!'
DOUBLE_SYMBOLS = '== != <= >='.split()
DIGITS = string.digits
IDENTIFIERS = string.ascii_letters + '_'

def is_keyword(c):
	return c in KEYWORDS

def is_symbol(c):
	return c in SYMBOLS

def is_double_symbol(c):
	return c in DOUBLE_SYMBOLS

def is_whitespace(c):
	return c in WHITESPACE

def is_identifier(c):
	return c in IDENTIFIERS

def is_digit(c):
	return c in DIGITS


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
			return EOT
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


template = open('template').read()
scanner = Scanner(template)
tokens = []

c = scanner.get_char()

in_block = False
html = []

while c != EOT:
	if in_block:  # actual lexing of language elements
		val = c.value
		# block closing characters
		if val == '}':
			# consume next char
			c2 = scanner.get_char()
			if c2.value == '}':
				in_block = False
			else:
				sys.exit('Bad character.')
			c = scanner.get_char()
		
		# whitespace
		elif is_whitespace(val):
			c = scanner.get_char()
		
		# identifiers
		elif is_identifier(val):
			identifier = val
			c = scanner.get_char()
			while is_identifier(c.value) or is_digit(c.value):
				identifier += c.value
				c = scanner.get_char()
			if is_keyword(identifier):
				tokens.append(Token(identifier, TOK_KEYWORD))
			else:
				tokens.append(Token(identifier, TOK_ID))
		
		# digits
		elif is_digit(val):
			num = val
			c = scanner.get_char()
			while is_digit(c.value):
				num += c.value
				c = scanner.get_char()
			# check if last character is an identifier
			if is_identifier(c.value):
				sys.exit('Invalid identifier after number: {!r}'.format(c.value))
			else:
				tokens.append(Token(num, TOK_DIGIT))
		
		# operators
		elif is_symbol(val):
			op = val
			c = scanner.get_char()
			if is_double_symbol(op + c.value):
				tokens.append(Token(op + c.value, TOK_SYMBOL))
				c = scanner.get_char()
			else:
				tokens.append(Token(op, TOK_SYMBOL))
		else:
			sys.exit('Not a valid character: {!r}'.format(c.value))
	else: # not inside a template tag
		if c.value == '{':
			# consume next char
			c2 = scanner.get_char()
			if c2.value == '{':
				in_block = True
				tokens.append(Token(''.join(html), TOK_HTML))
				html = []
			else:
				# not a block, so append the two read chars
				# '{' and something else
				html.append(c.value)
				html.append(c2.value)
		else:
			html.append(c.value)
		c = scanner.get_char()

if not in_block:
	# remaining chars
	tokens.append(Token(''.join(html), TOK_HTML))

for x in tokens:
	print(x)
