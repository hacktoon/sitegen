import stamper.parser as stamp

tpl = '''<html> 

{% 
	for page in pages:
		print page.title + '\n';
		print page.content + '\n';
		print '-' * 10  + '\n';
	end
 %}

</html>'''

p = stamp.Parser(tpl)
t = p.parse()
context = {'nome': 'joao', 'pages': [
	{'title': 'primeiro post', 'content': 'lalalala conteudo velho'},
	{'title': 'segundo post', 'content': 'super novidades'}
]}
print(t.render(context))
