<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0"
    xmlns:atom="http://www.w3.org/2005/Atom"
>
<channel>
    <title>{{site_title}}</title>
    <atom:link href="{{link}}" rel="self" type="application/rss+xml" />
    <link>{{link}}</link>
    <description>{{description}}</description>
    <lastBuildDate>{{build_date | fmt=%a, %d %b %Y %H:%M:%S +0000}}</lastBuildDate>
    {{list src=feeds}}
        <item>
		    <title>{{title}}</title>
		    <link>{{permalink}}</link>
		    <pubDate>{{date | fmt=%a, %d %b %Y %H:%M:%S +0000}}</pubDate>
		    <description><![CDATA[{{content}}]]></description>
		    <guid>{{permalink}}</guid>
		</item>
    {{end}}
</channel>
</rss>
