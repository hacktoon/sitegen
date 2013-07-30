
EOL = '\n'
EOF = '\0'

class Char():
	def __init__(self, line, col, val):
		self.line = line
		self.col = col
		self.val = val
	
	def __str__(self):
		return "Line {}, column {} - {!r}".format(
			self.line,
			self.col,
			self.val)


class Scanner():
	def __init__(self, template):
		self.template = template
		self.index = 0
		self.line = 1
		self.column = 1

	def get_char(self):
		if self.index >= len(self.template):
			return EOF
		c = self.template[self.index]
		if c == EOL:
			self.line += 1
			self.column = 1
		else:
			self.column += 1
		self.index += 1
		return Char(self.line, self.column, c)


template = open('template').read()
scanner = Scanner(template)
print(scanner.get_char())
