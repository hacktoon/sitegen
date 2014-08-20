import stamper.parser as parser

tpl = '''<html> 
{% 
	x = 5; 
	function soma(a,b) {
		return a+b;
	}
%}
<h1>teste</h1>
	{% print soma(1,2); %}
</html>
'''

p = parser.Parser(tpl)
t = p.parse()
t.render({'a': 32})
