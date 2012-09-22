# Ion - Shocking simple static (site) generator

## About
Static site generators are softwares that produces HTML and other static web formats like JSON as output. This output is then served just like the early years of web, what makes it fast. Content and templates are kept separated in different files, so changes are easy to make.

The advantages of static site generators are:
* Security - No database, no user input, nothing. Just plain old HTML.
* Performance - As I said, it's just HTML. Servers will love you.
* Easy to migrate/copy from/to anywhere. It's just a bunch of plain files.
* Easy to track changes and maintain websites with version controls systems like git.

And the disadvantages:
* No comments, pingbacks, search, contact forms or anything dynamic (although most of this itens can be implemented with third party services like Disqus)
* Not very user-friendly, but we are working on that.

Given these facts, static site generators are systems you can use for specific cases.

## Quickstart
You only need Python 3 to run Ion.

### How to install
Call **ion.py plug** in a directory in your web root. It will create the basic configuration to run your site.

### Configure
After installing, Ion will setup some basic configuration to you, but you can change these values.

Open the *config.ini* in **_ion** folder and define your settings. Here are some examples:
* **base_url** - Will be used for absolute linking.
* **default_theme** - If a custom theme is not provided for a page, this theme will be used.
* **blocked_dirs** - The directories you don't want Íon to read.
* **rss_items** - The max number of posts to be listed on RSS feed.
* **date_format** - A standard [date format](http://docs.python.org/library/datetime.html#strftime-and-strptime-behavior) used by Python language.
* **utc_offset** - The UTC offset to specify your time zone.

### Create your first page
Just run the *spark* command in the site root folder to create a new page:

    python3 ion.py spark
    
To create a different page, you have to pass a path as second parameter:

    python3 ion.py spark path/to/folder

This will create a *data.ion* model file. You're ready to start adding your own content:

    title = My first post
    date = 20/05/2012
    tags = proton, neutron, electron
    content
    My page content

Now run the *charge* command. The *charge* command accepts a path parameter just like the *spark*.
    
    python3 ion.py charge

This will create a HTML and a JSON file in the folder you specified. Done!

### Theming and page variables.
You can add new themes to **_ion/themes**, create and use optional variables without having to edit all your previous *.ion* files. If you want a page to use a specific theme, just add the definition in *data.ion*:

    title = My first post
    theme = mytheme
    css = main.css
    js = jquery.js, site.js
    date = 2012-05-20
    tags = shocking, blue
    content
    My page content

Defining new variables is as simple as that. Just add any new definition to your *data.ion*...

    author = Bob

... and get its value in the template:

    {{author}}

New themes must obey the same file structure of the default theme.

### And another thing...
* All page content stay in its own folder - so each page is independent.
* Uses the file system hierarchy to simulate pages and sub-pages.

## Help

Run **ion.py help**.
