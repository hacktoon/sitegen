import stamper.parser as stamp

tpl = '''<html> 

{% rlist pages as page: 
	if page.age > 2:  %}
	<p> {% print page.title; %} </p>
	<p> {% print page.content; %} </p>
	{% end %}
{% end %}

</html>'''

p = stamp.Parser(tpl)
t = p.parse()
context = {'nome': 'joao', 'pages': [
	{'title': 'primeiro post', 'content': 'lalalala conteudo velho', 'age': 85},
	{'title': 'segundo post', 'content': 'super novidades', 'age': 40},
	{'title': 'terceiro post', 'content': 'muita coisa', 'age': 15}
]}
print(t.render(context))
