import stamper.parser as stamp

tpl = '''<html>
{% use "base.html" %}
{% region"body":
 	list pages as page:
		if (page.age >= 16):  %}
			<p> {{ page.title }} </p>
			<p> {{ page.content }} </p>
		{% else: %}
			<p> {{ 'cant list' }} </p>
		{% end
	end
	print false
	print not true
end %}

</html>'''

p = stamp.Parser(tpl)
t = p.parse()
context = {'nome': 'joao', 'pages': [
	{'title': 'primeiro post', 'content': 'lalalala conteudo velho', 'age': 85},
	{'title': 'segundo post', 'content': 'super novidades', 'age': 40},
	{'title': 'terceiro post', 'content': 'muita coisa', 'age': 15}
]}
print(t.render(context))
