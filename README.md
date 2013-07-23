# Mnemonix - The Static Publishing System of Nimus Ages

## About
Mnemonix is a static web publisher.

## Quickstart
You only need Python 3 to run Mnemonix.

### Creating a site
Create a directory to be your web root. Enter it and call the following command:
    
	mnemonix init

### Configure
After installing, Mnemonix will setup some basic configuration to you, but you must change these values.

Open the *site* config file and define your settings. Here are some examples:
* **site_tags** - Tags used in HTML meta tags
* **base_url** - Will be used for absolute linking.
* **default_template** - If a custom template is not provided for a page, this one will be used.
* **feed_num** - Number of items to be listed in feeds

### Create your home page
Just run the *add* command in the site root folder to create a new page:

    mnemonix add .
    
To create a different page, you have to pass a path as second parameter:

    mnemonix add path/to/folder

This will create a *page* model file. You're ready to start adding your own content:

    title = My first post
    date = 2012-11-20 10:23:52
    tags = proton, neutron, electron
    content
    My page content

Now run the *gen* command to generate the pages.
    
    mnemonix gen

This will create (by default) a HTML and a JSON file in the folder you specified. Done!

## Customizing
### Templates and page variables
You can add new templates to **templates** folder, create and use optional variables without having to edit all your previous *page* files. If you want a page to use a specific template, just add the definition in **page**:

    title = My first post
    template = article
    date = 2012-11-20 10:23:52
    content
    My page content

This will make Mnemonix search for a file named **article.tpl** in templates folder. The template property is inherited by its children, so you don't have to manually configure each subpage under a common page.
Defining new variables is as simple as that. Just add any new definition to your *page* file...

    author = Bob

... and print its value in the template:

    {{author}}

### Styles and scripts
If a page uses specific CSS or Javascript files, they can be put in the page's folder and listed in the **page** file:

	styles = main.css
	scripts = jquery.js, site.js

They will be printed in the template through the variables {{styles}} and {{scripts}}.

### Page properties
Properties listed in a page data file can be used to change how Mnemonix will manage the page.

* nojson - Mnemonix will not generate a JSON file.
* nohtml - Mnemonix will not generate a HTML file.
* nolist - The page will not appear in listings
* nofeed - The page will not be listed in feeds.
* draft - The page will not be generated, listed or syndicated in feeds.
* group - This page's children pages will be defined as a group.

Example:

	props = nojson, nolist

### Page groups
Groups can be used to provide pagination, filter pages in listings and feeds. To define a group, you have to add the 'group' key to the page props definition in **page** file:

	props = group, nofeed, ...

### Collections and template listings
By default, Mnemonix provides some collections of data for using in templates. The first is the **pages** collection. You can list a subset of the pages of your site by passing arguments in the template tag:

	{{list src=pages num=10}}
        <li>{{title}}</li>
    {{end}}

The **children** collection lists all the child pages of the current page being generated.

	{{list src=children sort=date}}
        <li>{{title}}</li>
    {{end}}

The list options can control the items that will be rendered:

* sort - The 'sort by' option. Can be any page property. Default: 'date'.
* ord - Order of listing. Can be 'asc' or 'desc'. It only works if a sort parameter is passed. Default: 'asc'.
* group - Filter by group. The group is the URL name of the page where it was defined.
* num - Range of pages or the last x pages.

Examples:

    {{list src=pages group=blog num=6}}
		<li>{{title}}</li>
	{{end}}

Renders the last 6 pages of the 'blog' group.

	{{list src=pages sort=date ord=desc num=1:7}}
		<li>{{title}}</li>
	{{end}}

Renders the pages from 1st to 7th array position in decrescent order of date.
