<!DOCTYPE html>
<html>
<head>
    <meta name="author" content="{{print site_author}}" />
    <meta name="description" content="{{print site_description}}" />
    <meta name="keywords" content="{{print tags}}" />
    <meta charset="UTF-8" />
    <link rel="stylesheet" href="{{print themes_url}}bolt/bolt.css" type="text/css" />
    {{print css}}
    <title>{{print title}} | {{print site_name}}</title>
</head>
<body>
    <div id="wrapper">
        <header>
            <h1><a href="{{print base_url}}">{{print site_name}}</a></h1>
            <p id="description">{{print site_description}}</p>
        </header>
        <section id="content">
            <article>
                <h2><a href="{{print permalink}}">{{print title}}</a></h2>
                <span class="date">{{print date}}</span>
                <div class="entry">{{print content}}</div>
                Tags: <span class="tags">{{print tags}}</span>
            </article>
        </section>
        <section id="sidebar">
            <div class="widget">
                <h2>Last pages</h2>
                <ul>{{pagelist 15}}</ul>
            </div>
            <div class="widget">
                <h2>Last posts in blog</h2>
                <ul>{{pagelist 10 blog}}</ul>
            </div>
        </section>
        <footer>
            Bolt theme - by {{print site_author}}
        </footer>
    </div>
    {{print js}}
</body>
</html>
