# Ion - Shocking simple static (site) generator

## About
Static site generators are systems that reads a content source and given a template, produces HTML and other static web formats like JSON as output. This output is then served just like the early years of web, what makes it fast. Content and templates are kept separated in different files, so changes are easy to make.

The advantages of static site generators are:
* Security - No database, no user input, nothing. Just plain old HTML.
* Performance - As said above, it's just HTML. Servers will love you.
* Easy to migrate/copy from/to anywhere. It's just a bunch of plain files.
* Easy to track changes and maintain websites with version control systems like git.

And the disadvantages:
* No comments, pingbacks, search, contact forms or anything dynamic (although most of this itens can be implemented with third party services like Disqus)
* Not very user-friendly, but we are working on that.

Given these facts, static site generators are systems you can use for specific cases.

## Quickstart
You only need Python 3 to run Ion.

### Creating a site
Create a directory to be your web root. Enter it and call the following command:
    
	ion init

### Configure
After installing, Ion will setup some basic configuration to you, but you must change these values.

Open the *config.ion* in and define your settings. Here are some examples:
* **site_tags** - Tags used in HTML meta tags
* **base_url** - Will be used for absolute linking.
* **default_theme** - If a custom theme is not provided for a page, this theme will be used.
* **feed_num** - Number of items to be listed in feeds

### Create your home page
Just run the *add* command in the site root folder to create a new page:

    ion add
    
To create a different page, you have to pass a path as second parameter:

    ion add path/to/folder

This will create a *data.ion* model file. You're ready to start adding your own content:

    title = My first post
    date = 2012-11-20 10:23:52
    tags = proton, neutron, electron
    content
    My page content

Now run the *gen* command to generate the pages.
    
    ion gen

This will create (by default) a HTML and a JSON file in the folder you specified. Done!

## Customizing
### Theming and page variables
You can add new themes to **themes** folder, create and use optional variables without having to edit all your previous *.ion* files. If you want a page to use a specific theme, just add the definition in **data.ion**:

    title = My first post
    theme = mytheme
    date = 2012-11-20 10:23:52
    tags = shocking, blue
    content
    My page content

Defining new variables is as simple as that. Just add any new definition to your *data.ion*...

    author = Bob

... and get its value in the template:

    {{author}}

New themes must obey the same file structure of the default theme.

### Styles and scripts
If a page uses specific CSS or Javascript files, they can be put in the page's folder and listed in the **data.ion** file:

	styles = main.css
	scripts = jquery.js, site.js

They will be printed in the template through the variables {{styles}} and {{scripts}}.

### Page properties
Properties listed in a page data file can be used to change how Ion will handle the page.

* nojson - Ion will not generate a JSON file.
* nohtml - Ion will not generate a HTML file.
* nolist - The page will not appear in listings
* norender - The page will not be generated. Better to use it with 'nolist'
* nofeed - The page will not be listed in feeds.
* group - This page's children pages will be defined as a group.

Example:

	props = nojson, nolist

### Page groups
Groups can be used to apply properties to several pages at once, provide pagination and page filtering in listings. To define a group, thus enabling sorting and pagination of its child pages, you have to add the 'group' key to the page props definition in **data.ion** file:

	props = group, nofeed, ...

To define group properties, choose a page whose children you want to modify. Just add the common properties to the **data.ion** file with the "group_" prefix.

	group_template = main
	group_theme = blog

These properties will be applied to all pages under the chosen page.

### Templates
A theme can have multiples template files under the same theme. By default Ion uses the **main.tpl** file. You can create new *tpl* files in the theme folder and select it in the **data.ion** config without the extension:

    template = archive

### Collections and template listings
By default, Ion provides some collections of data for using in templates. The first is the **pages** collection. You can list a subset of the pages of your site by passing arguments in the template tag:

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
* group - Filter by group. The group is the name of the page where it was defined.
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
