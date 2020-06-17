# Sitegen

## About
Sitegen is a static web generator.

## Quickstart
You only need Python 3 to run Sitegen.

### Creating a site
Create a directory to be your web root. Enter it and call the following command:

	sitegen build

### Configure
After installing, Sitegen will setup some basic configuration to you, but you must change these values.

Open the *site* config file and define your settings. Here are some examples:
* **tags** - Tags used in HTML meta tags
* **base_url** - Will be used for absolute linking.
* **default_template** - If a custom template is not provided for a page, this one will be used.
* **feed_num** - Number of items to be listed in feeds
* **blocked_dirs** - List of directories separated by comma that Sitegen won't read.

### Create your home page
Just run the *write* command in the site root folder to create a new page:

    sitegen write .

To create a different page, you have to pass a path as second parameter:

    sitegen write path/to/folder

This will create a *page* model file. You're ready to start adding your own content:

    title = My first post
    date = 2012-11-20 10:23:52
    tags = proton, neutron, electron
    content
    My page content

The HTML comment tag <!-- more --> can be used to define a limit to distinguish the excerpt from the content.

	This is the excerpt
	<!-- more -->
	This is the rest of the content

Now run the *publish* command to generate the pages.

    sitegen publish

This will create (by default) a HTML and a JSON file in the folder you specified. Done!

## Customizing
### Templates and page variables
You can add new templates to **templates** folder, create and use optional variables without having to edit all your previous *page* files. If you want a page to use a specific template, just add the definition in **page**:

    title = My first post
    template = article
    date = 2012-11-20 10:23:52
    content
    My page content

This will make Sitegen search for a file named **article.tpl** in templates folder. The template property is inherited by its children, so you don't have to manually configure each subpage under a common page.
Defining new variables is as simple as that. Just add any new definition to your *page* file...

    author = Bob

... and print its value in the template:

    {{page.author}}

### Styles and scripts
If a page uses specific CSS or Javascript files, they can be put in the page's folder and listed in the **page** file:

	styles = [main.css]
	scripts = [jquery.js, site.js]

They will be printed in the template through the variables {{page.styles}} and {{page.scripts}}.

### Page properties
Properties listed in a page data file can be used to change how Sitegen will manage the page.

* nojson - Sitegen will not generate a JSON file.
* nohtml - Sitegen will not generate a HTML file.
* nolist - The page will not appear in listings
* nofeed - The page will not be listed in feeds.
* draft - The page will not be generated, listed or syndicated in feeds.

Example:

	props = [nojson, nolist]

### Categories
Categories can be used to provide pagination, filter pages in listings and feeds. To define a category, you have to add the 'category' key in **page** file:

	category = my_category

### Collections and template listings
By default, Sitegen provides some collections of data for using in templates. The first is the **pages** collection. You can list a subset of the pages of your site by passing arguments in the template tag:

	{% list pages as page: %}
        <li>{{page.title}}</li>
    {% end %}

You can limit the number of itens that will be listed:

	{% list pages as page limit 10: %}
        <li>{{page.title}}</li>
    {% end %}

Or reverse the list printing order using `rlist`:

	{% rlist pages as page limit 10: %}
        <li>{{page.title}}</li>
    {% end %}
