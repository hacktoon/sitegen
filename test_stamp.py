import stamper.parser as stamp

tpl = '''<html> 

{% list pages as page: %}
	<p> {% print page.title; %} </p>
	<p> {% print page.content; %} </p>		
{% end %}

</html>'''

p = stamp.Parser(tpl)
t = p.parse()
context = {'nome': 'joao', 'pages': [
	{'title': 'primeiro post', 'content': 'lalalala conteudo velho'},
	{'title': 'segundo post', 'content': 'super novidades'}
]}
print(t.render(context))
