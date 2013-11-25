<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
    <title>{{site.title}}</title>
    <atom:link href="{{feed.link}}" rel="self" type="application/rss+xml" />
    <link>{{feed.link}}</link>
    <description>{{site.description}}</description>
    <lastBuildDate>{{feed.build_date fmt="%a, %d %b %Y %H:%M:%S +0000"}}</lastBuildDate>
    {% pagelist %}
        <item>
		    <title>{{each.title}}</title>
		    {% if var="each.permalink" equals="http://localhost/about/page2" %}
				<link>{{each.permalink}}</link>
			{% end %}
		    <pubDate>{{each.date fmt="%a, %d %b %Y %H:%M:%S +0000"}}</pubDate>
		    <description><![CDATA[{{each.content}}]]></description>
		    <guid>{{each.permalink}}</guid>
		</item>
    {%end%}
</channel>
</rss>
