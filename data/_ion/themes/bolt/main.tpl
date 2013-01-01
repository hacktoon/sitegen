<!DOCTYPE html>
<html>
<head>
    <meta name="author" content="{{site_author}}" />
    <meta name="description" content="{{site_description}}" />
    <meta name="keywords" content="{{tags}}" />
    <meta charset="UTF-8" />
    <link rel="stylesheet" href="{{themes_url}}bolt/bolt.css" type="text/css" />
    {{css}}
    <title>{{title}} | {{site_name}}</title>
</head>
<body>
    <div id="wrapper">
        <header>
            <h1><a href="{{base_url}}">{{site_name}}</a></h1>
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
                <span class="date">{{date}}</span>
                <div class="entry">{{content}}</div>
                Tags: <span class="tags">{{tags}}</span>
            </article>
        </section>
        {{include menu}}
        <footer>
            Bolt theme - by {{site_author}}
        </footer>
    </div>
    {{js}}
</body>
</html>
