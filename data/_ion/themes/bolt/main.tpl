<!DOCTYPE html>
<html>
<head>
    <meta name="author" content="{{print site_author}}" />
    <meta name="description" content="{{print site_description}}" />
    <meta name="keywords" content="{{print tags}}" />
    <meta charset="UTF-8" />
    <link rel="stylesheet" href="{{print themes_url}}bolt/ion.css" type="text/css" />
    {{print css}}
    <title>{{print title}} | {{print site_name}}</title>
</head>
<body>
    <h1><a href="{{print base_url}}">{{print site_name}}</a></h1>
    <p>{{print site_description}}</p>
    <ul>
        <li><a href="{{print base_url}}">Home</a></li>
        <li><a href="{{print base_url}}about">About</a></li>
        {{pagelist 3}}
    </ul>
    <h2><a href="{{print permalink}}">{{print title}}</a></h2>
    <span>{{print date}}</span>
    <p>{{print content}}</p>
    <h2>Included menu</h2>
    <p>{{include footer}}</p>
    {{print js}}
</body>
</html>
