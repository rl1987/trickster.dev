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

Let us explore how to use Beautiful Soup for web scraping. We start by using
the lxml parser on a simple HTML document.

```
$ python3
Python 3.11.5 (main, Aug 24 2023, 15:09:45) [Clang 14.0.3 (clang-1403.0.22.14.1)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> from bs4 import BeautifulSoup
>>> soup = BeautifulSoup(html_str, 'lxml')
>>> soup
<html><head><title>Title!</title></head><body><h1>The Title</h1></body></html>
>>> type(soup)
<class 'bs4.BeautifulSoup'>
```

We can regenerate the HTML document in a pretty-printed form:

```
>>> print(soup.prettify())
<html>
 <head>
  <title>
   Title!
  </title>
 </head>
 <body>
  <h1>
   The Title
  </h1>
 </body>
</html>
```

We can use object properties to traverse across the tree structure and extract
stuff we may want to parse:

```
>>> soup.title
<title>Title!</title>
>>> soup.title.text
'Title!'
>>> soup.title.name
'title'
>>> soup.body.h1.text
'The Title'
```

To provide an example on how to run queries, let us have a bigger HTML document
to parse:

```html
<html>
    <head>
        <title>Product list</title>
    </head>
    <body>
        <table border="1">
            <thead>
                <tr>
                    <th>Product name</th>
                    <th>Price</th>
                    <th>URL</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td id="productname" class="productname">Jordan 4 Retro</td>
                    <td id="price">$269</td>
                    <td><a id="pdpurl" href="https://stockx.com/air-jordan-4-retro-red-cement">link</a></td>
                </tr>
                <tr>
                    <td id="productname" class="productname">adidas Yeezy Boost 350 V2 Static (Non-Reflective) (2018/2023)</td>
                    <td id="price">$195</td>
                    <td><a id="pdpurl" href="https://stockx.com/adidas-yeezy-boost-350-v2-static">link</a></td>
                </tr>
            </tbody>
        </table>
    </body>
</html>
```

Now we can use `find()` method to find a single result or `find_all()` to find
multiple results:

```
>>> in_f = open("test.html", "r")
>>> html_str = in_f.read()
>>> in_f.close()
>>> soup = BeautifulSoup(html_str, "lxml")
>>> soup.find('title')
<title>Product list</title>
>>> soup.find_all(class_='productname')
[<td class="productname" id="productname">Jordan 4 Retro</td>, <td class="productname" id="productname">adidas Yeezy Boost 350 V2 Static (Non-Reflective) (2018/2023)</td>]
>>> soup.find_all(id='price')
[<td id="price">$269</td>, <td id="price">$195</td>]
```


