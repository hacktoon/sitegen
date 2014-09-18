import stamper.parser as stamp
import re

filename = 'tpl.html'
tpl = open(filename).read()
p = stamp.Parser(tpl, filename=filename)
t = p.parse()
context = {'nome': 'joao', 'pages': [
	{'title': 'primeiro post', 'content': 'lalalala conteudo velho', 'age': 85},
	{'title': 'segundo post', 'content': 'super novidades', 'age': 40},
	{'title': 'terceiro post', 'content': 'muita coisa', 'age': 15},
	{'title': 'post nerdson 1', 'content': 'nerdson 1', 'category': 'nerdson', 'age': 15},
	{'title': 'post nerdson 2', 'content': 'nerdson 2', 'category': 'nerdson', 'age': 15},
	{'title': 'post nerdson 3', 'content': 'nerdson 3', 'category': 'nerdson', 'age': 15},
	{'title': 'post nerdson 4', 'content': 'nerdson 4', 'category': 'nerdson', 'age': 15}
]}

print(t.render(context))