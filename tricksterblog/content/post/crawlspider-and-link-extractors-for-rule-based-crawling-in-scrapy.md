+++
author = "rl1987"
title = "CrawlSpider and link extractors for rule-based crawling in Scrapy"
date = "2023-05-02"
draft = true
tags = ["scraping", "python", "scrapy"]
+++

The [front page of Scrapy project](https://scrapy.org/) provides a basic example
of Scrapy spider:

```python
class BlogSpider(scrapy.Spider):
    name = 'blogspider'
    start_urls = ['https://www.zyte.com/blog/']

    def parse(self, response):
        for title in response.css('.oxy-post-title'):
            yield {'title': title.css('::text').get()}

        for next_page in response.css('a.next'):
            yield response.follow(next_page, self.parse)
```

In this code snippet, crawling is performed imperatively - link to next page
is extracted and from it a new request is generated. However, Scrapy also
supports another, declarative, approach of crawling that is based on
setting crawling rules for the spider and letting it follow links without
explicit request generation. This abstracts away the link traversal and
enables us to focus on data extraction aspect. 

To use this approach in our code, we must be familiar with `LinkExtractor`
objects and `CrawlSpider` class. Let us start with the former. For the sake 
of the example, we will be doing a little scraping of 
[books.toscrape.com](http://books.toscrape.com/index.html) - a simple site that
is made to be scraped.

A link extractor is an object that processes a Scrapy `Response` object and
extracts a list of links according to some criteria (URL substrings, regexes,
XPaths, CSS selectors, subdomains). It returns the extracted links as a list
of `Link` objects. Each `Link` object contains not only the absolute URL, 
but also some additional information: anchor text, URL fragment, `nofollow`
flag.

Let us use Scrapy shell to see how link extractors can be created and used:

```
In [1]: fetch("https://books.toscrape.com/")
2023-05-02 13:05:41 [scrapy.core.engine] INFO: Spider opened
2023-05-02 13:05:42 [scrapy.core.engine] DEBUG: Crawled (200) <GET https://books.toscrape.com/> (referer: None)

In [2]: from scrapy.linkextractors import LinkExtractor

In [3]: book_link_extractor = LinkExtractor(allow='index.html', deny=['catalogue/page', 'catalogue/category/books', 'https://books.toscrape.com/index.html'])

In [4]: for link in book_link_extractor.extract_links(response):
   ...:     print(link)
   ...: 
Link(url='https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html', text='', fragment='', nofollow=False)
Link(url='https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html', text='', fragment='', nofollow=False)
Link(url='https://books.toscrape.com/catalogue/soumission_998/index.html', text='', fragment='', nofollow=False)
Link(url='https://books.toscrape.com/catalogue/sharp-objects_997/index.html', text='', fragment='', nofollow=False)
Link(url='https://books.toscrape.com/catalogue/sapiens-a-brief-history-of-humankind_996/index.html', text='', fragment='', nofollow=False)
Link(url='https://books.toscrape.com/catalogue/the-requiem-red_995/index.html', text='', fragment='', nofollow=False)
Link(url='https://books.toscrape.com/catalogue/the-dirty-little-secrets-of-getting-your-dream-job_994/index.html', text='', fragment='', nofollow=False)
Link(url='https://books.toscrape.com/catalogue/the-coming-woman-a-novel-based-on-the-life-of-the-infamous-feminist-victoria-woodhull_993/index.html', text='', fragment='', nofollow=False)
Link(url='https://books.toscrape.com/catalogue/the-boys-in-the-boat-nine-americans-and-their-epic-quest-for-gold-at-the-1936-berlin-olympics_992/index.html', text='', fragment='', nofollow=False)
Link(url='https://books.toscrape.com/catalogue/the-black-maria_991/index.html', text='', fragment='', nofollow=False)
Link(url='https://books.toscrape.com/catalogue/starving-hearts-triangular-trade-trilogy-1_990/index.html', text='', fragment='', nofollow=False)
Link(url='https://books.toscrape.com/catalogue/shakespeares-sonnets_989/index.html', text='', fragment='', nofollow=False)
Link(url='https://books.toscrape.com/catalogue/set-me-free_988/index.html', text='', fragment='', nofollow=False)
Link(url='https://books.toscrape.com/catalogue/scott-pilgrims-precious-little-life-scott-pilgrim-1_987/index.html', text='', fragment='', nofollow=False)
Link(url='https://books.toscrape.com/catalogue/rip-it-up-and-start-again_986/index.html', text='', fragment='', nofollow=False)
Link(url='https://books.toscrape.com/catalogue/our-band-could-be-your-life-scenes-from-the-american-indie-underground-1981-1991_985/index.html', text='', fragment='', nofollow=False)
Link(url='https://books.toscrape.com/catalogue/olio_984/index.html', text='', fragment='', nofollow=False)
Link(url='https://books.toscrape.com/catalogue/mesaerion-the-best-science-fiction-stories-1800-1849_983/index.html', text='', fragment='', nofollow=False)
Link(url='https://books.toscrape.com/catalogue/libertarianism-for-beginners_982/index.html', text='', fragment='', nofollow=False)
Link(url='https://books.toscrape.com/catalogue/its-only-the-himalayas_981/index.html', text='', fragment='', nofollow=False)
```

We fetched the front page of the site, imported `LinkExtractor` class and
initialised an extractor for links pointing to what eCommerce people would
call Product Detail Pages (PDPs). The `allow` and `deny` values of 
`LinkExtractor` constructor arguments are written so that they narrow down
the exact links we need. Note that we can allow or deny links based on a single
substring or a list of them. Once we have the link extractor created, we 
call it's `extract_links()` method on a response object we got from fetching
the page, which gives us a list of `Link` objects. We can see that all the links
point to book details pages.

But we also need a link to the next Product List Page. Extracting it is also
quite simple with another link extractor:

```
In [5]: next_page_link_extractor = LinkExtractor(allow='catalogue/page')

In [6]: next_page_link_extractor.extract_links(response)
Out[6]: [Link(url='https://books.toscrape.com/catalogue/page-2.html', text='next', fragment='', nofollow=False)]
```

Now that we are familiar with link extractors, let us learn about the 
`CrawlSpider`. Let's use the Scrapy CLI to generate all the boilerplate for
Scrapy project and a new spider class from the `crawl` template:

```
$ scrapy startproject sample .
$ scrapy genspider -t crawl books books.toscrape.com
```

In sample/spiders/books.py file we have the following starter code:

```python
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class BooksSpider(CrawlSpider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["http://books.toscrape.com/"]

    rules = (Rule(LinkExtractor(allow=r"Items/"), callback="parse_item", follow=True),)

    def parse_item(self, response):
        item = {}
        #item["domain_id"] = response.xpath('//input[@id="sid"]/@value').get()
        #item["name"] = response.xpath('//div[@id="name"]').get()
        #item["description"] = response.xpath('//div[@id="description"]').get()
        return item
```

This is a bit different than the default starter code you get from the 
default template. `BooksSpider` class is inheriting from 
[`CrawlSpider`](https://docs.scrapy.org/en/latest/topics/spiders.html?highlight=CrawlSpider#scrapy.spiders.CrawlSpider) class
(which is a subclass of `scrapy.Spider`). It has a `rules` property with a tuple
of [`Rule`](https://docs.scrapy.org/en/latest/topics/spiders.html?highlight=CrawlSpider#scrapy.spiders.Rule) 
objects (just a single entry at this point) and no `parse()` method,
as the `parse()` method is overriden in the `CrawlSpider` class.
We also got one callback method that is referenced in the rule by name.

Let us use this code as starting point to try out the rule-based crawling
on our target site:

```python
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class BooksSpider(CrawlSpider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["http://books.toscrape.com/"]

    rules = (
        Rule(LinkExtractor(allow='index.html', 
                           deny=[
                               'catalogue/page', 
                               'catalogue/category/books', 
                               'https://books.toscrape.com/index.html']
                           ), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow='catalogue/page'), follow=True)
    )


    def parse_item(self, response):
        item = {}

        item['title'] = response.xpath('//h1/text()').get()
        item['price'] = response.xpath('//div[contains(@class, "product_main")]/p[@class="price_color"]/text()').get()
        item['url'] = response.url
        
        return item

```

In the `rules` tuple we got two [`Rule`](https://docs.scrapy.org/en/latest/topics/spiders.html?highlight=CrawlSpider#scrapy.spiders.Rule) 
objects that are based on link extractors
we tried out earlier. The first rule is based on PDP link extractor and 
references the `parse_item()` callback method. The second one is merely for
traversing to next page of the book list and is not directly associated with
data extraction. Thus it references no callback method. Since the objective
here is to demonstrate rule-based crawling we only extract a couple of fields
from the book details page.

Running this spider scrapes the entire site without us having to explicitly
generate requests to progress the crawling further. We see log lines like:

```
2023-05-02 13:23:20 [scrapy.core.engine] DEBUG: Crawled (200) <GET http://books.toscrape.com/catalogue/page-2.html> (referer: http://books.toscrape.com/)
2023-05-02 13:23:20 [scrapy.core.engine] DEBUG: Crawled (200) <GET http://books.toscrape.com/catalogue/its-only-the-himalayas_981/index.html> (referer: http://books.toscrape.com/)
2023-05-02 13:23:20 [scrapy.core.engine] DEBUG: Crawled (200) <GET http://books.toscrape.com/catalogue/libertarianism-for-beginners_982/index.html> (referer: http://books.toscrape.com/)
2023-05-02 13:23:20 [scrapy.core.engine] DEBUG: Crawled (200) <GET http://books.toscrape.com/catalogue/mesaerion-the-best-science-fiction-stories-1800-1849_983/index.html> (referer: http://books.toscrape.com/)
2023-05-02 13:23:20 [scrapy.core.engine] DEBUG: Crawled (200) <GET http://books.toscrape.com/catalogue/olio_984/index.html> (referer: http://books.toscrape.com/)
2023-05-02 13:23:20 [scrapy.core.engine] DEBUG: Crawled (200) <GET http://books.toscrape.com/catalogue/our-band-could-be-your-life-scenes-from-the-american-indie-underground-1981-1991_985/index.html> (referer: http://books.toscrape.com/)
2023-05-02 13:23:20 [scrapy.core.scraper] DEBUG: Scraped from <200 http://books.toscrape.com/catalogue/its-only-the-himalayas_981/index.html>
{'title': "It's Only the Himalayas", 'price': '£45.17', 'url': 'http://books.toscrape.com/catalogue/its-only-the-himalayas_981/index.html'}
2023-05-02 13:23:20 [scrapy.core.scraper] DEBUG: Scraped from <200 http://books.toscrape.com/catalogue/libertarianism-for-beginners_982/index.html>
{'title': 'Libertarianism for Beginners', 'price': '£51.33', 'url': 'http://books.toscrape.com/catalogue/libertarianism-for-beginners_982/index.html'}
2023-05-02 13:23:20 [scrapy.core.scraper] DEBUG: Scraped from <200 http://books.toscrape.com/catalogue/mesaerion-the-best-science-fiction-stories-1800-1849_983/index.html>
{'title': 'Mesaerion: The Best Science Fiction Stories 1800-1849', 'price': '£37.59', 'url': 'http://books.toscrape.com/catalogue/mesaerion-the-best-science-fiction-stories-1800-1849_983/index.html'}
2023-05-02 13:23:20 [scrapy.core.scraper] DEBUG: Scraped from <200 http://books.toscrape.com/catalogue/olio_984/index.html>
{'title': 'Olio', 'price': '£23.88', 'url': 'http://books.toscrape.com/catalogue/olio_984/index.html'}
2023-05-02 13:23:20 [scrapy.core.scraper] DEBUG: Scraped from <200 http://books.toscrape.com/catalogue/our-band-could-be-your-life-scenes-from-the-american-indie-underground-1981-1991_985/index.html>
{'title': 'Our Band Could Be Your Life: Scenes from the American Indie Underground, 1981-1991', 'price': '£57.25', 'url': 'http://books.toscrape.com/catalogue/our-band-could-be-your-life-scenes-from-the-american-indie-underground-1981-1991_985/index.html'}
2023-05-02 13:23:21 [scrapy.core.engine] DEBUG: Crawled (200) <GET http://books.toscrape.com/catalogue/how-music-works_979/index.html> (referer: http://books.toscrape.com/catalogue/page-2.html)
2023-05-02 13:23:21 [scrapy.core.engine] DEBUG: Crawled (200) <GET http://books.toscrape.com/catalogue/chase-me-paris-nights-2_977/index.html> (referer: http://books.toscrape.com/catalogue/page-2.html)
2023-05-02 13:23:21 [scrapy.core.engine] DEBUG: Crawled (200) <GET http://books.toscrape.com/catalogue/in-her-wake_980/index.html> (referer: http://books.toscrape.com/catalogue/page-2.html)
2023-05-02 13:23:21 [scrapy.core.engine] DEBUG: Crawled (200) <GET http://books.toscrape.com/catalogue/aladdin-and-his-wonderful-lamp_973/index.html> (referer: http://books.toscrape.com/catalogue/page-2.html)
```

To learn more about link extractors and rule-based crawling, read the following
pages of Scrapy documentation:

* [Link Extractors](https://docs.scrapy.org/en/latest/topics/link-extractors.html#link-extractors)
* [Spiders](https://docs.scrapy.org/en/latest/topics/spiders.html)

