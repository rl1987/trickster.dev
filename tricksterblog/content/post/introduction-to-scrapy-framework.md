+++
author = "rl1987"
title = "Introduction to Scrapy framework"
date = "2022-02-14"
draft = true
tags = ["web-scraping", "scrapy", "python"]
+++

[Scrapy](https://scrapy.org/) is a Python framework for web scraping. One might ask: why would we need an entire framework
for web scraping if we can simply code up some simple scripts in Python using Beautiful Soup, lxml, requests and the like?
To be fair, for simple scrapers you don't. However when you are developing and running web scraper of non-trivial complexity the
following problems will arise:

* Error handling. If you have an unhandled exception in your Python code, it can bring down an entire script, which can cause
to time and data being lost. Furthermore, you will need to make sure your requests are running with timeouts as sometimes
remote servers fail to respond at all. This is not a major issue in small web scraping operations, but at large enough scale
low probability events are bound to happen. For example, you may be scraping one million pages and have one of 100 000 requests
fail. You need to make sure that this small fraction of failed requests do not bring down the entire script.
* Concurrency. Generally speaking, it is not efficient to do one request at a time, as your code will spend most of the time
waiting for response from the server. To speed up the scraping, it is highly desirable to use multithreading or asynchronuous
code so that multiple requests are running in parallel.
* Separation of concerns between scraping the data and further processing. 

Scrapy framework addresses these problems as follows:

* Scrapy is designed in such a way that unhandled exceptions are logged for troubleshooting, but does not crash the entire
scraping job. Furthermore, it provides infrastructure for handling some of the HTTP-level error conditions.
* Scrapy is based on [Twisted](https://www.twistedmatrix.com/trac/) framework for asynchronuous network programming and
supports concurrent requests out of the box.
* Scrapy is architected to allow decoupling of scraping part from further processing of scraped data and provides easy to use
boilerplate code for development.

The primary way to install Scrapy is to use PIP command `pip3 install scrapy`. Some Linux distributions may also ship it through
their package managers (e.g. APT on Ubuntu), but the version might be lagging behind the last official release from the Scrapy
project.

Scrapy shell and selectors
--------------------------

Once you install Scrapy you can access it's own REPL by running `scrapy shell`. This provides an interactive environment for 
exploration and experimentation. For example, `fetch` command downloads a given page into response object:

```
In [1]: fetch('https://books.toscrape.com/')
2022-02-13 14:41:22 [scrapy.core.engine] INFO: Spider opened
2022-02-13 14:41:23 [scrapy.core.engine] DEBUG: Crawled (200) <GET https://books.toscrape.com/> (referer: None)

In [2]: response
Out[2]: <200 https://books.toscrape.com/>
```

Note that you can also launch Scrapy shell from the command line of your OS with URL of the page you want fetched:

```
$ scrapy shell https://books.toscrape.com/
```

Now we can try running some XPath or CSS queries on Scrapy response object. However, doing so will not return string with text
or HTML snippet. It will return an object called selector list:

```
In [1]: response.xpath("//title")
Out[1]: [<Selector xpath='//title' data='<title>\n    All products | Books to S...'>]

In [2]: type(response.xpath("//title"))
Out[2]: scrapy.selector.unified.SelectorList
```

Unsurprisingly, selector list is a list of selector objects:

```
In [3]: type(response.xpath("//title")[0])
Out[3]: scrapy.selector.unified.Selector
```

Scrapy selector object encapsulates XPath/CSS query and provides methods to get matching parts of HTML document. Calling `.get()`
method on selector or selector list gives you the contents of the first matched element:

```
In [4]: response.xpath("//title").get()
Out[4]: '<title>\n    All products | Books to Scrape - Sandbox\n</title>'

In [5]: response.xpath("//title")[0].get()
Out[5]: '<title>\n    All products | Books to Scrape - Sandbox\n</title>'

```

We can see that we are getting the HTML string of matched element, but not the contents of the tag. Scrapy framework expects us
to adjust the query accordingly if we want just the contents:

```
In [6]: response.xpath("//title/text()").get()
Out[6]: '\n    All products | Books to Scrape - Sandbox\n'

In [7]: response.xpath("string(//title)").get()
Out[7]: '\n    All products | Books to Scrape - Sandbox\n'

```

We can also chain the `.xpath()` or `.css()` calls on the selectors to perform extraction in step-by-step fashion:

```
In [8]: response.xpath("/html").css('title').xpath('text()').get()
Out[8]: '\n    All products | Books to Scrape - Sandbox\n'
```

Selector object also has a `.re()` method for running regular expressions. However, this does not return a new selector and gives
you a list of strings instead:

```
In [9]: response.selector.re('\d{1,}\.\d{2}')
Out[9]:
['51.77',
 '53.74',
 '50.10',
 '47.82',
 '54.23',
 '22.65',
 '33.34',
 '17.93',
 '22.60',
 '52.15',
 '13.99',
 '20.66',
 '17.46',
 '52.29',
 '35.02',
 '57.25',
 '23.88',
 '37.59',
 '51.33',
 '45.17']
```

Scrapy selector does not provide the HTML element text directly. However, we can get attributes through `.attrib` property:

```
In [10]: response.xpath('//a')[0].attrib
Out[10]: {'href': 'index.html'}
```

To get all results from the selector call the `.getall()` method on it:

```
In [11]: response.xpath('//a/@href').getall()
Out[11]:
['index.html',
 'index.html',
 'catalogue/category/books_1/index.html',
 'catalogue/category/books/travel_2/index.html',
 'catalogue/category/books/mystery_3/index.html',
 'catalogue/category/books/historical-fiction_4/index.html',
 'catalogue/category/books/sequential-art_5/index.html',
 'catalogue/category/books/classics_6/index.html',
 'catalogue/category/books/philosophy_7/index.html',
 'catalogue/category/books/romance_8/index.html',
...
```

Scrapy shell is very useful tool for trying out and refining your XPath/CSS queries even if the final code you are developing
will not be based on Scrapy. 

Scrapy Spider
-------------

Now we're getting close to develop some actual code, but we need to get familiar with one of the central concepts in Scrapy:
the spider. Spider is an object that performs link traversal (crawling) and data extraction from web pages. Developing custom
spiders (that is, your own subclasses of `scrapy.Spider` object) is most of the work you will be doing when using Scrapy.
The front page of Scrapy website provides an example of very basic spider that traverses blog pages and extracts post titles:

```
import scrapy

class BlogSpider(scrapy.Spider):
    name = 'blogspider'
    start_urls = ['https://www.zyte.com/blog/']

    def parse(self, response):
        for title in response.css('.oxy-post-title'):
            yield {'title': title.css('::text').get()}

        for next_page in response.css('a.next'):
            yield response.follow(next_page, self.parse)
```

Each spider has to have `name` property filled with it's name and `start_urls` property set to list of initial URLs that scraping
will start from. By default, spider will start by iterating across this list and scheduling requests for each URL in the list.
For each valid response, `parse()` method will be called (this is by default and can be overriden). 404 erros and other invalid
responses will be filtered out. Callback method (`parse()` in this example) is called for each valid response that is received.
This is where response parsing and data extraction happens. In this example, a CSS query to extract blog titles is implemented.
For each title, the code yields an item dictionary.

We have two important concepts here:

* Item is an unit of scraped data that spider generates. It's a scraped data point, basically.
* `yield` keyword in Python means "lazy return". In async code it is used to postpone the execution of all preceding code until
the exact moment when result is needed. 

This spider also performs another CSS query to find links to further pages to be scraped. For each of these links, new request
is being generated. This is how you schedule the scraping of further pages based on the links you have found on the current page.





WRITEME: items

WRITEME: pipelines

WRITEME: middlewares

WRITEME: more on Scrapy CLI

