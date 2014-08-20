import stamper.parser as stamp

tpl = '''<html> 
{% 
	x = 5;
	function soma(a,b) {
		return a+b;
	}
%}
<h1>{%print nome;   %}</h1>
	{% y= soma(1,56) ; 
	print y;
	%}
</html>'''

p = stamp.Parser(tpl)
t = p.parse()
print(t.render({'nome': 'joao'}))
