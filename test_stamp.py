import stamper.parser as stamp

tpl = '''<html> 
{%  
	a = 23;
	x_b = 1;
	if a > 20: parse "menu.html"; end
	if a < 20: print 'oooi 2'; end
%}
<h1>{%print $x_b; %}</h1>


</html>'''

p = stamp.Parser(tpl)
t = p.parse()
context = {'nome': 'joao', 'page': {'title': 'post original', 'content': 'lalalala conteudo velho'}}
print(t.render(context))
