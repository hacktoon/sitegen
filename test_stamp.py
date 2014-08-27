import stamper.parser as stamp

tpl = '''<html> 

{% 
	for page in pages:
		print page.title + '\n';
		print page.content;
	end
 %}

</html>'''

p = stamp.Parser(tpl)
t = p.parse()
context = {'nome': 'joao', 'pages': [
	{'title': 'post original', 'content': 'lalalala conteudo velho'},
	{'title': 'post velho', 'content': 'super novidades'}
]}
print(t.render(context))
