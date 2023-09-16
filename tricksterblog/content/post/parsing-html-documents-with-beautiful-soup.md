+++
author = "rl1987"
title = "Parsing HTML documents with Beautiful Soup"
date = "2023-09-20"
draft = true
tags = ["scraping", "python"]
+++

Beautiful Soup (also known as `bs4`) is a Python module for parsing HTML (and
also XML) documents. It is commonly used in web scraper development. Beautiful
Soup takes an HTML string and parses it into a tree structure that reflects
the structure of DOM tree, but has properties and methods related to 
accessing data and running queries. 

We can install it via PIP as `beautifulsoup4`. Furthermore, some operating 
systems ship Beautiful Soup it in via their package managers. For example, 
there's `python3-bs4` package on Debian APT.

Beautiful Soup does not perform parsing on it's own. Instead, it uses a lower
level HTML/XML parsing library and converts the results into it's own data model.
As of September 2023, there are following options for the HTML parsing library:

* Python's vanilla HTML parser (`html.parser`) - middling performance and
average tolerance to malformed HTML.
* `lxml` - Python wrapper around libxml2 C library - very good performance,
quite lenient for bad HTML.
* `html5lib` - Pure Python HTML5 parser that is slow, but can deal with some
pretty messed up pages.

Let us explore how to use Beautiful Soup for web scraping.

WRITEME
