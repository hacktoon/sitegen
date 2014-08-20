import stamper.parser as parser

tpl = '''<html> 
{{ x = 5; }}
<h1>teste</h1>
{{
print x;
print a;
}}
</html>
'''
tpl = '''x=5; 
if x == 5 {
	print x;
} else { 
	print "eee";
}


'''

p = parser.Parser(tpl)
t = p.parse()
t.render({'a': 32})
