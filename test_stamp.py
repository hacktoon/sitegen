import stamper.parser

filename = 'tpl.html'
tpl = open(filename).read()

class Stamper:
	def __init__(self, tpl, filename=''):
		self.tpl = tpl
		self.filename = filename

	def render(self, content):
		parse_tree = stamper.parser.Parser(tpl, filename=filename).parse()
		return parse_tree.render(context)

context = {'nome': 'joao', 'pages': [
	{'title': 'primeiro post', 'content': 'lalalala conteudo velho', 'age': 85},
	{'title': 'segundo post', 'content': 'super novidades', 'age': 40},
	{'title': 'terceiro post', 'content': 'muita coisa', 'age': 15},
	{'title': 'post nerdson 1', 'content': 'nerdson 1', 'category': 'nerdson', 'age': 15},
	{'title': 'post nerdson 2', 'content': 'nerdson 2', 'category': 'nerdson', 'age': 15},
	{'title': 'post nerdson 3', 'content': 'nerdson 3', 'category': 'nerdson', 'age': 15},
	{'title': 'post nerdson 4', 'content': 'nerdson 4', 'category': 'nerdson', 'age': 15}
]}

stamp = Stamper(tpl, filename)
print(stamp.render(context))