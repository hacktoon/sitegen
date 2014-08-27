import stamper.parser as stamp

tpl = '''<html> 

{% 
	x = 1;
	if x > 1:
		print 'oi';
	else:
		print 'nao';
	end

	parse "menu.html";

	function soma(a,b):
		print a+b;
	end

	print soma(1,2);
 %}

</html>'''

p = stamp.Parser(tpl)
t = p.parse()
context = {'nome': 'joao', 'pages': [
	{'title': 'post original', 'content': 'lalalala conteudo velho'},
	{'title': 'post velho', 'content': 'super novidades'}
]}
print(t.render(context))
