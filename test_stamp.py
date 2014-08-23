import stamper.parser as stamp

tpl = '''<html> 
{%  
	a = 23;
	x = 1;
	if a > 20: parse "menu.html"; end
	if a < 20: print 'oooi 2'; end
%}
<h1>{%print nome; %}</h1>


</html>'''

p = stamp.Parser(tpl)
t = p.parse()
context = {'nome': 'joao', 'pages': [
	{'title': 'post original', 'content': 'lalalala conteudo velho'},
	{'title': 'post segundo', 'content': 'conteudo mais novo'}
]}
print(t.render(context))
