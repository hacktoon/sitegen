import stamper.parser as parser

tpl = '''<html> 
{% x = 5; %}
<h1>teste</h1>
	{% print x; %}
</html>
'''

tpl2 = '''x=5;
y=3; 
if x == 5 {
	if y == 3 {
		print 4;
	}
}
'''

p = parser.Parser(tpl)
t = p.parse()
t.render({'a': 32})
