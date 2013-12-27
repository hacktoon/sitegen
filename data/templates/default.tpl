<!DOCTYPE html>
<html>
<head>
	<meta name="author" content="{{site.author}}" />
	<meta name="description" content="{{site.description}}" />
	<meta name="keywords" content="{{site.tags}} {{page.tags}}" />
	<meta charset="UTF-8" />
	<link rel="stylesheet" href="{{site.base_url}}templates/default.css" type="text/css" />
	{{page.styles}}
	<title>{{page.title}} | {{site.title}}</title>
</head>
<body>
	<div id="wrapper">
		<header>
			<h1><a href="{{site.base_url}}">{{site.title}}</a></h1>
			<p id="description">{{site.description}}</p>
		</header>
		<section id="content">
			<article>
				<h2><a href="{{page.url}}">{{page.title}}</a></h2>
				<span class="date">{{page.date fmt="%Y-%m-%d %H:%M:%S"}}</span>
				<div class="entry">{{page.content}}</div>
				Tags: <span class="tags">{{page.tags}}</span>
			</article>
		</section>
		{%include file="menu"%}
		<footer>
			Main theme - by {{site.author}}
		</footer>
	</div>
	{{page.scripts}}
</body>
</html>
