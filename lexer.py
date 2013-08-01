import re
import sys

EOL = '\n'
EOT = '\0'

TOK_HTML = 'HTML'
TOK_SYMBOL = 'Symbol'
TOK_ID = 'Identifier'
TOK_DIGIT = 'Digit'
TOK_KEYWORD = 'Keyword'

def is_keyword(c):
	regex = re.compile(r'if|else|endif|loop|endloop|say|partial|set|include|and|not|or')
	return regex.search(c)

def is_symbol(c):
	regex = re.compile(r'[-+*/=()%<>!]')
	return regex.search(c)

def is_whitespace(c):
	regex = re.compile(r'\s')
	return regex.search(c)

def is_identifier(c):
	regex = re.compile(r'[a-zA-Z_]')
	return regex.search(c)

def is_digit(c):
	regex = re.compile(r'[0-9]')
	return regex.search(c)


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
	if in_block:
		if c.value == '}':
			# consume next char
			c2 = scanner.get_char()
			if c2.value == '}':
				in_block = False
			else:
				sys.exit('Bad character.')

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
