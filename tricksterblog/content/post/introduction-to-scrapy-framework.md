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

```python
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

Let us use Scrapy CLI to generate a new Scrapy project with a single spider to scrape [books.toscrape.com](https://books.toscrape.com) -
a simple to site built for people to practice their web scraping skills.

```
$ scrapy startproject books_to_scrape
New Scrapy project 'books_to_scrape', using template directory '/usr/local/lib/python3.9/site-packages/scrapy/templates/project', created in:
    /Users/[REDACTED]/src/tmp/books_to_scrape

You can start your first spider with:
    cd books_to_scrape
    scrapy genspider example example.com
$ cd books_to_scrape/
$ scrapy genspider books books.toscrape.com
Created spider 'books' using template 'basic' in module:
  books_to_scrape.spiders.books
```

This gives us the following directory structure:

```
$ tree .
.
├── books_to_scrape
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-39.pyc
│   │   └── settings.cpython-39.pyc
│   ├── items.py
│   ├── middlewares.py
│   ├── pipelines.py
│   ├── settings.py
│   └── spiders
│       ├── __init__.py
│       ├── __pycache__
│       │   └── __init__.cpython-39.pyc
│       └── books.py
└── scrapy.cfg

4 directories, 11 files
```

In books.py we have the following boilerplate code that we will use as a starting point:

```python
import scrapy


class BooksSpider(scrapy.Spider):
    name = 'books'
    allowed_domains = ['books.toscrape.com']
    start_urls = ['http://books.toscrape.com/']

    def parse(self, response):
        pass
```

However, first we need to take a look at the site we are going to scrape and do some planning on the overall scraping strategy.
On the side there's a list of book categories. For each category there's a paginated list of books that we can iterate across.
You may notice that entire list of books is also available from the front page. This does indeed make things easier for us, but 
that won't be the case for all eCommerce sites. Thus we will be proceeding with slightly harder two-tiered approach of going through
categories first and scraping the book (product) pages for each category. For each product (book) page we will be running XPath
queries to extract product details.

Let us write code that implements the crawling aspect first. 

```python
    def start_requests(self):
        yield scrapy.Request(self.start_urls[0], callback=self.parse_categories)

    def parse_categories(self, response):
        for category_link in response.xpath('//div[@class="side_categories"]//a'):
            category_url = urljoin(response.url, category_link.attrib.get('href'))
            yield scrapy.Request(category_url, callback=self.parse_book_list)

    def parse_book_list(self, response):
        for book_link in response.xpath('//article[@class="product_pod"]/h3/a'):
            book_url = urljoin(response.url, book_link.attrib.get('href'))
            yield scrapy.Request(book_url, callback=self.parse_book_page)

        next_page_link = response.xpath('//li[@class="next"]/a')
        if next_page_link is not None:
            next_page_url = urljoin(response.url, next_page_link.attrib.get('href'))
            yield scrapy.Request(next_page_url, callback=self.parse_book_list)

    def parse_book_page(self, response):
        pass
```

Since we have three custom callback methods (one for front page, another for product list page, and yet another for 
product details page) we override the `start_requests()` method to generate a request for front page with the 
corresponding callback. This callback method, `parse_categories()` extracts category links grom left hand side of 
the page and generates requests for scraping them. We use `urljoin()` from `urllib.parse` module to convert relative URLs 
into absolute form and we yield a new request for each category link with `parse_book_list()` method being the callback for
all new requests.

Next callback method, `parse_book_list()`, deals with book list page. This time, we are primarily concerned with links to product
pages. We use the same approach to extract them and to schedule a new request. Since the site implements pagination, we may also
have a link to next page. If it is found, one more request is generated with the same callback method that we're discussing now.

Lastly, there's one more callback method that will be used to parse the product page. It's empty for now. 

To check that everything goes well, we can run `scrapy runspider` command with the path to spider file and check the log lines.
We can see that it starts by visiting front page, then goes across category links. We can also see that duplicate(s) has been 
filtered out:

```
$ scrapy runspider spiders/books.py 
2022-02-13 16:09:30 [scrapy.utils.log] INFO: Scrapy 2.5.1 started (bot: books_to_scrape)
2022-02-13 16:09:30 [scrapy.utils.log] INFO: Versions: lxml 4.7.1.0, libxml2 2.9.12, cssselect 1.1.0, parsel 1.6.0, w3lib 1.22.0, Twisted 20.3.0, Python 3.9.10 (main, Jan 15 2022, 11:48:04) - [Clang 13.0.0 (clang-1300.0.29.3)], pyOpenSSL 21.0.0 (OpenSSL 1.1.1l  24 Aug 2021), cryptography 36.0.0, Platform macOS-12.1-x86_64-i386-64bit
2022-02-13 16:09:30 [scrapy.utils.log] DEBUG: Using reactor: twisted.internet.selectreactor.SelectReactor
2022-02-13 16:09:30 [scrapy.crawler] INFO: Overridden settings:
{'BOT_NAME': 'books_to_scrape',
 'EDITOR': 'vim',
 'NEWSPIDER_MODULE': 'books_to_scrape.spiders',
 'ROBOTSTXT_OBEY': True,
 'SPIDER_LOADER_WARN_ONLY': True,
 'SPIDER_MODULES': ['books_to_scrape.spiders']}
2022-02-13 16:09:30 [scrapy.extensions.telnet] INFO: Telnet Password: d4e8f3a322620d99
2022-02-13 16:09:30 [scrapy.middleware] INFO: Enabled extensions:
['scrapy.extensions.corestats.CoreStats',
 'scrapy.extensions.telnet.TelnetConsole',
 'scrapy.extensions.memusage.MemoryUsage',
 'scrapy.extensions.logstats.LogStats']
2022-02-13 16:09:30 [scrapy.middleware] INFO: Enabled downloader middlewares:
['scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware',
 'scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware',
 'scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware',
 'scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware',
 'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware',
 'scrapy.downloadermiddlewares.retry.RetryMiddleware',
 'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware',
 'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware',
 'scrapy.downloadermiddlewares.redirect.RedirectMiddleware',
 'scrapy.downloadermiddlewares.cookies.CookiesMiddleware',
 'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware',
 'scrapy.downloadermiddlewares.stats.DownloaderStats']
2022-02-13 16:09:30 [scrapy.middleware] INFO: Enabled spider middlewares:
['scrapy.spidermiddlewares.httperror.HttpErrorMiddleware',
 'scrapy.spidermiddlewares.offsite.OffsiteMiddleware',
 'scrapy.spidermiddlewares.referer.RefererMiddleware',
 'scrapy.spidermiddlewares.urllength.UrlLengthMiddleware',
 'scrapy.spidermiddlewares.depth.DepthMiddleware']
2022-02-13 16:09:30 [scrapy.middleware] INFO: Enabled item pipelines:
[]
2022-02-13 16:09:30 [scrapy.core.engine] INFO: Spider opened
2022-02-13 16:09:30 [scrapy.extensions.logstats] INFO: Crawled 0 pages (at 0 pages/min), scraped 0 items (at 0 items/min)
2022-02-13 16:09:30 [scrapy.extensions.telnet] INFO: Telnet console listening on 127.0.0.1:6025
2022-02-13 16:09:30 [scrapy.core.engine] DEBUG: Crawled (404) <GET http://books.toscrape.com/robots.txt> (referer: None)
2022-02-13 16:09:31 [scrapy.core.engine] DEBUG: Crawled (200) <GET http://books.toscrape.com/> (referer: None)
2022-02-13 16:09:31 [scrapy.core.engine] DEBUG: Crawled (200) <GET http://books.toscrape.com/catalogue/category/books_1/index.html> (referer: http://books.toscrape.com/)
2022-02-13 16:09:31 [scrapy.core.engine] DEBUG: Crawled (200) <GET http://books.toscrape.com/catalogue/category/books/sports-and-games_17/index.html> (referer: http://books.toscrape.com/)
2022-02-13 16:09:31 [scrapy.core.engine] DEBUG: Crawled (200) <GET http://books.toscrape.com/catalogue/category/books/religion_12/index.html> (referer: http://books.toscrape.com/)
2022-02-13 16:09:31 [scrapy.core.engine] DEBUG: Crawled (200) <GET http://books.toscrape.com/catalogue/category/books/childrens_11/index.html> (referer: http://books.toscrape.com/)
2022-02-13 16:09:31 [scrapy.dupefilters] DEBUG: Filtered duplicate request: <GET http://books.toscrape.com/catalogue/category/books/sports-and-games_17/index.html> - no more duplicates will be shown (see DUPEFILTER_DEBUG to show all duplicates)
...
```

Duplicate filtering is yet another helpful thing that Scrapy does for us so that we don't have to. 

Soon enough it reaches product pages by traversing the links. Let us implement that `parse_book_page()` method:

```python
    def parse_book_page(self, response):
        item = dict()
        
        item['title'] = response.xpath('//h1/text()').get()
        item['upc'] = response.xpath('//tr[./th[contains(text(), "UPC")]]/td/text()').get()
        item['description'] = response.xpath('//article[@class="product_page"]/p/text()').get()
        item['price_excl_tax'] = response.xpath('//tr[./th[contains(text(), "Price (excl. tax)")]]/td/text()').get()
        item['price_incl_tax'] = response.xpath('//tr[./th[contains(text(), "Price (incl. tax)")]]/td/text()').get()
        item['availability'] = response.xpath('//tr[./th[contains(text(), "Availability")]]/td/text()').get()
        item['n_reviews'] = response.xpath('//tr[./th[contains(text(), "Number of reviews")]]/td/text()').get()

        yield item
```

First we instantiate the item dictionary, then we run a few of XPath queries to extract several pieces of information about product:
title, UPC, description, price, availability, number of reviews - the typical stuff that customers in eCommerce industry are
interested in. Lastly, we yield the item dictionary.

Let us run the spider again. This time, we expect some actual data to be scraped. Thus we specify output CSV file path through
Scrapy CLI:

```
$ scrapy runspider spiders/books.py -o books.csv
```

Now we start seeing some product information being logged into the terminal, which shows that data extraction is working:

```
...
2022-02-13 16:15:32 [scrapy.core.engine] DEBUG: Crawled (200) <GET http://books.toscrape.com/catalogue/the-last-girl-the-dominion-trilogy-1_70/index.html> (referer: http://books.toscrape.com/catalogue/category/books/science-fiction_16/index.html)
2022-02-13 16:15:33 [scrapy.core.scraper] DEBUG: Scraped from <200 http://books.toscrape.com/catalogue/choosing-our-religion-the-spiritual-lives-of-americas-nones_14/index.html>
{'title': "Choosing Our Religion: The Spiritual Lives of America's Nones", 'upc': 'a812f6969ddf3e39', 'description': 'To the dismay of religious leaders, study after study has shown a steady decline in affiliation and identification with traditional religions in America. By 2014, more than twenty percent of adults identified as unaffiliated--up more than seven percent just since 2007. Even more startling, more than thirty percent of those under the age of thirty now identify as "Nones"--a To the dismay of religious leaders, study after study has shown a steady decline in affiliation and identification with traditional religions in America. By 2014, more than twenty percent of adults identified as unaffiliated--up more than seven percent just since 2007. Even more startling, more than thirty percent of those under the age of thirty now identify as "Nones"--answering "none" when queried about their religious affiliation. Is America losing its religion? Or, as more and more Americans choose different spiritual paths, are they changing what it means to be religious in the United States today? In Choosing Our Religion, Elizabeth Drescher explores the diverse, complex spiritual lives of Nones across generations and across categories of self-identification as "Spiritual-But-Not-Religious," "Atheist," "Agnostic," "Humanist," "just Spiritual," and more. Drawing on more than one hundred interviews conducted across the United States, Drescher opens a window into the lives of a broad cross-section of Nones, diverse with respect to age, gender, race, sexual orientation, and prior religious background. She allows Nones to speak eloquently for themselves, illuminating the processes by which they became None, the sources of information and inspiration that enrich their spiritual lives, the practices they find spiritually meaningful, how prayer functions in spiritual lives not centered on doctrinal belief, how morals and values are shaped outside of institutional religions, and how Nones approach the spiritual development of their own children. These compelling stories are deeply revealing about how religion is changing in America--both for Nones and for the religiously affiliated family, friends, and neighbors with whom their lives remain intertwined. ...more', 'price_excl_tax': '£28.42', 'price_incl_tax': '£28.42', 'availability': 'In stock (1 available)', 'n_reviews': '0'}
2022-02-13 16:15:33 [scrapy.core.scraper] DEBUG: Scraped from <200 http://books.toscrape.com/catalogue/having-the-barbarians-baby-ice-planet-barbarians-75_23/index.html>
{'title': "Having the Barbarian's Baby (Ice Planet Barbarians #7.5)", 'upc': '6717a70913b3db79', 'description': 'Megan’s ready to give birth, but she’s not ready to let her mate leave her side. When Cashol must go hunting to feed the tribe, they’re separated for the first time since resonance. Not a problem, except the baby’s ready to be born and there’s a storm brewing… This is a short story set in the ICE PLANET BARBARIANS world. It does not stand alone, and is intended to be read Megan’s ready to give birth, but she’s not ready to let her mate leave her side. When Cashol must go hunting to feed the tribe, they’re separated for the first time since resonance. Not a problem, except the baby’s ready to be born and there’s a storm brewing…\u2029\u2029 This is a short story set in the ICE PLANET BARBARIANS world. It does not stand alone, and is intended to be read after BARBARIAN’S MATE. It’s a little bit of sweetness for those that can’t get enough of the big blue aliens! Happy reading! ...more', 'price_excl_tax': '£34.96', 'price_incl_tax': '£34.96', 'availability': 'In stock (1 available)', 'n_reviews': '0'}
2022-02-13 16:15:33 [scrapy.core.scraper] DEBUG: Scraped from <200 http://books.toscrape.com/catalogue/the-book-of-mormon_571/index.html>
{'title': 'The Book of Mormon', 'upc': '3f25a2fedae191cc', 'description': 'The Book of Mormon is a volume of scripture comparable to the Bible. It is a record of God\'s dealings with the ancient inhabitants of the Americas and contains, as does the Bible, the fullness of the everlasting gospel.The book was written by many ancient prophets by the spirit of prophecy and revelation. Their words, written on gold plates, were quoted and abridged by a p The Book of Mormon is a volume of scripture comparable to the Bible. It is a record of God\'s dealings with the ancient inhabitants of the Americas and contains, as does the Bible, the fullness of the everlasting gospel.The book was written by many ancient prophets by the spirit of prophecy and revelation. Their words, written on gold plates, were quoted and abridged by a prophet-historian named Mormon. The record gives an account of two great civilizations. One came from Jerusalem in 600 B.C., and afterward separated into two nations, known as the Nephites and the Lamanites. The other came much earlier when the Lord confounded the tongues at the Tower of Babel. This group is known as the Jaredites. After thousands of years, all were destroyed except the Lamanites, and they are among the ancestors of the American Indians. The crowning event recorded in the Book of Mormon is the personal ministry of the Lord Jesus Christ among the Nephites soon after his resurrection. It puts forth the doctrines of the gospel, outlines the plan of salvation, and tells men what they must do to gain peace in this life and eternal salvation in the life to come. After Mormon completed his writings, he delivered the account to his son Moroni, who added a few words of his own and hid up the plates in the hill Cumorah. On September 21, 1823, the same Moroni, then a glorified, resurrected being, appeared to the Prophet Joseph Smith and instructed him relative to the ancient record and its destined translation into the English language. In due course the plates were delivered to Joseph Smith, who translated them by the gift and power of God. The record is now published in many languages as a new and additional witness that Jesus Christ is the Son of the living God and that all who will come unto him and obey the laws and ordinances of his gospel may be saved. Concerning this record the Prophet Joseph Smith said: "I told the brethren that the Book of Mormon was the most correct of any book on earth, and the keystone of our religion, and a man would get nearer to God by abiding by its precepts, than by any other book." In addition to Joseph Smith, the Lord provided for eleven others to see the gold plates for themselves and to be special witnesses of the truth and divinity of the Book of Mormon. Their written testimonies are included herewith as "The Testimony of Three Witnesses" and "The Testimony of Eight Witnesses." We invite all men everywhere to read the Book of Mormon, to ponder in their hearts the message it contains, and the to ask God, the Eternal Father, in the name of Christ if the book is true. Those who pursue this course and ask in faith will gain a testimony of its truth and divinity by the power of the Holy Ghost. (See Moroni 10:3-5.) ...more', 'price_excl_tax': '£24.57', 'price_incl_tax': '£24.57', 'availability': 'In stock (9 available)', 'n_reviews': '0'}
...
```

Once this finishes, you will have a CSV file with the scraped data. However, if you launch the spider again it will not delete 
previously scraped data - new data will be appended to the file. This may not be desirable and you may want to take steps to 
prevent it.

Scrapy items
------------

So far regular Python dictionaries were used for items. However, there is more powerful way to create them. We can subclass
`scrapy.Item` class to create items in more object-oriented way. Scrapy project boilerplate includes items.py file with the 
following template code:

```python
# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BooksToScrapeItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
```

Let us update the code to use item objects. In items.py file we create item subclass with all the fields we need:

```python
class Book(scrapy.Item):
    title = scrapy.Field()
    upc = scrapy.Field()
    description = scrapy.Field()
    price_excl_tax = scrapy.Field()
    price_incl_tax = scrapy.Field()
    availability = scrapy.Field()
    n_reviews = scrapy.Field()
```

Since item API is made to be very similar to Python dictionary we won't be doing much changes on the spider code.

First change to spider is to import the `Book` item class:

```python
from books_to_scrape.items import Book
```

Next change is to instantiate a `Book` object instead of `dict`:

```python
    def parse_book_page(self, response):
        item = Book()
```

When we run the spider again we see that items are logged in more readable way. Furthermore, we are more prepared to implement
further post-processing of scraped data in Scrapy pipelines.

Scrapy pipelines
----------------

After scraping the data, you may want to peform data cleanup, filtering, enrichment and exporting. Item pipeline is a component
of Scrapy project that you would implement for one or more of post-processing tasks. Multiple pipelines may be implemented in a
single Scrapy project and executed sequentially - output of pipeline earlier in sequence would be the input of next next pipeline.
Newly created Scrapy project comes with a pipelines.py file with some basic template code for pipeline development:

```python
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class BooksToScrapePipeline:
    def process_item(self, item, spider):
        return item
```

Let us develop a basic pipeline to exemplify a simple cleanup of book data we are scraping:

```python
class BooksToScrapePipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        adapter['price_excl_tax'] = adapter['price_excl_tax'].replace('£', '')
        adapter['price_incl_tax'] = adapter['price_incl_tax'].replace('£', '')
        adapter['availability'] = adapter['availability'].replace('In stock (', '').replace(' available)', '')

        return item
```

We develop the `process_item()` method that Scrapy will call with our item. First, we wrap the item in the item adapter object
that provides an unified interface to various kinds of items (Python dictionaries, `scrapy.Item`-based objects, etc.) to 
enable them to be processed the same way. Next, we remove the pound character from price fields and clean the extra whitespace
from the availability field. Then we return the modified item.

To enable this pipeline, we need to edit settings.py. Since we kept the defautl pipeline class only we only need to uncomment
the following:

```python
ITEM_PIPELINES = {
    'books_to_scrape.pipelines.BooksToScrapePipeline': 300,
}
```

However, if wanted to implement more pipelines we would need to add more key-value pairs into `ITEM_PIPELINES` dictionary.
Key in this dictioary is pipeline class name, prefixed by module name. Value is a number used for pipeline ordering - pipelines
with lower number get executed earlier.

Pipelines can also be used to extract data to databases or other systems external to Scrapy project. They can also be used
to drop some of the items.

To see some more examples of Scrapy pipelines, take a look at: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

Scrapy middlewares
------------------

Scrapy also provides ways to hooking into HTTP requests that spider generates and hooking into responses before they reach the 
spider through components called middlewares. There are two kinds of middlewares that you can implement:

* Downloader middlewares hook into various points of HTTP request and response processing. They can be used for proxy pool
integration, lower level handling of HTTP messages, monitoring and debugging.
* Spider middlewares can hook into responses just before they reach spider. They can also hook into requests and items generation
from the spider. This can be used to enforce scraping limits and to implement other customisations for scraping/crawling.

Scrapy ships with several default middlewares for heeding robots.txt rules, managing cookies, controlling HTTP request headers
and other common tasks.

* https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
* https://docs.scrapy.org/en/latest/topics/spider-middleware.html

Scrapy CLI
----------

We are already familiar with Scrapy CLI commands to launch Scrapy shell and to generate project/spider. However there are few
more useful commands:

* `scrapy view` command downloads the page and opens it in the browser. This can be used for debugging to see the page in the
same way as spider receives it.
* `scrapy crawl` is similar to `scrapy runspider`, but it takes spider name instead of file path.
* `scrapy bench` runs a quick benchmark.

To learn more about Scrapy CLI, see: https://docs.scrapy.org/en/latest/topics/commands.html

