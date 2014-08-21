import stamper.parser as stamp

tpl = '''<html> 
{%  
	a = 3;
	x =1;
	if a > 20: print 'oooi'; end
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

soma(4, 1);

%}
</html>'''

p = stamp.Parser(tpl)
t = p.parse()
print(t.render({'nome': 'joao'}))
