import stamper.parser as stamp

tpl = '''<html> 
{%  
	print page . 
	title + '\n';
	print page.content;	
%}
</html>'''

p = stamp.Parser(tpl)
t = p.parse()
context = {'nome': 'joao', 'page': {'title': 'post original', 'content': 'lalalala conteudo velho'}}
print(t.render(context))
