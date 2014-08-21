import stamper.parser as stamp

tpl = '''<html> 
{%  
	a = 3;
	x =1;
	if a > 20: print 'oooi'; end
	if a < 20: print 'oooi 2'; end

	parse "menu.html";
%}
<h1>{% print nome;  %}</h1>
	{% if x == 5: %}
		<a>x eh 5</a>
	{% else: %}
		<a>x nao eh 5</a>
	{% end 

function soma(a,b):
	if a > b:
		return a+b;
	else:
		return 'respeite a ordem';
	end
end

i = 10;
while(i>0):
	print i;
	print '\n';
	i = i - 1;
end

print 'teste';
print soma(4, 1);

%}
</html>'''

p = stamp.Parser(tpl)
t = p.parse()
print(t.render({'nome': 'joao'}))
