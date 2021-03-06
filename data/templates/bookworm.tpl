<!DOCTYPE html>
<html>
<head>
	<meta name="author" content="{{site_author}}" />
	<meta name="description" content="{{site_description}}" />
	<meta name="keywords" content="{{site_tags}} {{tags}}" />
	<meta charset="UTF-8" />
	<link rel="stylesheet" href="{{base_url}}/templates/bookworm.css" type="text/css" />
	{{styles}}
	<title>{{title}} | {{site_title}}</title>
</head>
<body>
	<div id="wrapper">
		<header>
			<h1><a href="{{base_url}}">{{site_title}}</a></h1>
			<p id="description">{{site_description}}</p>
		</header>
		<section id="content">
			<ul id="breadcrumbs">
				{{breadcrumbs}}
					<li>
						<a title="{{title}}" href="{{permalink}}">
							{{title}}
						</a>
					</li>
				{{end}}
			</ul>
			<article>
				<h2><a href="{{permalink}}">{{title}}</a></h2>
				<span class="date">{{date | fmt=%Y-%m-%d %H:%M:%S}}</span>
				<div class="entry">{{content}}</div>
				Tags: <span class="tags">{{tags}}</span>
			</article>
		</section>
		{{include menu}}
		<footer>
			Bookworm theme - by {{site_author}}
		</footer>
	</div>
	{{scripts}}
</body>
</html>
