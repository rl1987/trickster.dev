+++
author = "rl1987"
title = "Turning Scrapy spider into API with ScrapyRT"
date = "2022-06-04"
tags = ["python", "scraping", "scrapy"]
+++

Scrapy framework provides many benefits over regular Python scripts when it comes
to developing web scrapers of non-trivial complexity. However Scrapy by itself does
provide a direct way to integrate your web scraper into larger system that may need
some on-demand scraping (e.g. price comparison website). 
[ScrapyRT](https://github.com/scrapinghub/scrapyrt) is a Scrapy extension
that was developed by Zyte to address this limitation. Just like Scrapy itself,
it is trivially installable through PIP. ScrapyRT exposes your Scrapy project
(not just spiders, but also pipelines, middlewares and extensions) through
HTTP API that you can integrate into your systems.

To show how ScrapyRT can be used, we are going to rely on 
[`books_to_scrape`](https://github.com/rl1987/trickster.dev-code/tree/main/2022-02-13-introduction-to-scrapy-framework/books_to_scrape)
Scrapy project that was developed to demonstrate Scrapy project development.

Launching ScrapyRT entails running a single command in Scrapy project root
directory:

```
$ cd books_to_scrape/
$ scrapyrt
2022-06-04 10:33:17+0200 [-] Log opened.
2022-06-04 10:33:17+0200 [-] Site starting on 9080
2022-06-04 10:33:17+0200 [-] Starting factory <twisted.web.server.Site object at 0x10aa7fa90>
2022-06-04 10:33:17+0200 [-] Running with reactor: SelectReactor. 
```

By default it binds the socket to local host interface. This will make it reachable
by software running on your local machine, but not by external clients that we may
want to expose the API to. Easy fix is to make it bind to wildcard IP address (0.0.0.0)
by providing the `--ip` command line argument:

```
$ scrapyrt --ip 0.0.0.0
```

Running ScrapyRT like this make it accessible through all IP addresses the IP
host can accept incoming traffic at.

Now let us use cURL to launch the spider:

```
$ curl "http://127.0.0.1:9080/crawl.json?spider_name=books&url=http://books.toscrape.com&callback=parse_categories"
```

We called the API at `/crawl.json` endpoint with arguments for spider name, 
URL to start scraping at and in this case we also need to provide callback
method name. Some seconds later we receive JSON response that can be piped 
into jq(1) or `python3 -m json.tool` for pretty-printing:

```
$ curl "http://127.0.0.1:9080/crawl.json?spider_name=books&url=http://books.toscrape.com&callback=parse_categories" | jq
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 1615k  100 1615k    0     0  54798      0  0:00:30  0:00:30 --:--:--  416k
{
  "status": "ok",
  "items": [
    {
      "title": "The Rise of Theodore Roosevelt (Theodore Roosevelt #1)",
      "upc": "1a5044d233936b1a",
      "description": "Selected by the Modern Library as one of the 100 best nonfiction books of all timeDescribed by the Chicago Tribune as \"a classic,\" The Rise of Theodore Roosevelt stands as one of the greatest biographies of our time. The publication of The Rise of Theodore Roosevelt on September 14th, 2001 marks the 100th anniversary of Theodore Roosevelt becoming president.",
      "price_excl_tax": "42.57",
      "price_incl_tax": "42.57",
      "availability": "3",
      "n_reviews": "0"
    },
...
    {
      "title": "Trespassing Across America: One Man's Epic, Never-Done-Before (and Sort of Illegal) Hike Across the Heartland",
      "upc": "2173a2ce35f6ace1",
      "description": "Told with sincerity, humor, and wit,Trespassing Across Americais both a fascinating account of one man’s remarkable journey along the Keystone XL pipeline and a meditation on climate change, the beauty of the natural world, and the extremes to which we can push ourselves—both physically and mentally. It started as a far-fetched idea—to hike the entire length of the propose Told with sincerity, humor, and wit, Trespassing Across America is both a fascinating account of one man’s remarkable journey along the Keystone XL pipeline and a meditation on climate change, the beauty of the natural world, and the extremes to which we can push ourselves—both physically and mentally.  It started as a far-fetched idea—to hike the entire length of the proposed route of the Keystone XL pipeline. But in the months that followed, it grew into something more for Ken Ilgunas. It became an irresistible adventure—an opportunity not only to draw attention to global warming but also to explore his personal limits. So in September 2012, he strapped on his backpack, stuck out his thumb on the interstate just north of Denver, and hitchhiked 1,500 miles to the Alberta tar sands. Once there, he turned around and began his 1,700-mile trek to the XL’s endpoint on the Gulf Coast of Texas, a journey he would complete entirely on foot, walking almost exclusively across private property.Both a travel memoir and a reflection on climate change, Trespassing Across America is filled with colorful characters, harrowing physical trials, and strange encounters with the weather, terrain, and animals of America’s plains. A tribute to the Great Plains and the people who live there, Ilgunas’s memoir grapples with difficult questions about our place in the world: What is our personal responsibility as stewards of the land? As members of a rapidly warming planet? As mere individuals up against something as powerful as the fossil fuel industry? Ultimately, Trespassing Across America is a call to embrace the belief that a life lived not half wild is a life only half lived. ...more",
      "price_excl_tax": "53.51",
      "price_incl_tax": "53.51",
      "availability": "3",
      "n_reviews": "0"
    }
  ],
  "items_dropped": [],
  "stats": {
    "downloader/request_bytes": 416236,
    "downloader/request_count": 1132,
    "downloader/request_method_count/GET": 1132,
    "downloader/response_bytes": 4427209,
    "downloader/response_count": 1132,
    "downloader/response_status_count/200": 1131,
    "downloader/response_status_count/404": 1,
    "dupefilter/filtered": 1051,
    "elapsed_time_seconds": 30.023132,
    "finish_reason": "finished",
    "finish_time": "2022-06-04 08:55:20",
    "httpcompression/response_bytes": 25118716,
    "httpcompression/response_count": 1132,
    "item_scraped_count": 1000,
    "log_count/DEBUG": 2133,
    "log_count/INFO": 9,
    "memusage/max": 82591744,
    "memusage/startup": 82591744,
    "request_depth_max": 51,
    "response_received_count": 1132,
    "robotstxt/request_count": 1,
    "robotstxt/response_count": 1,
    "robotstxt/response_status_count/404": 1,
    "scheduler/dequeued": 1131,
    "scheduler/dequeued/memory": 1131,
    "scheduler/enqueued": 1131,
    "scheduler/enqueued/memory": 1131,
    "start_time": "2022-06-04 08:54:50"
  },
  "spider_name": "books"
}
```

Not only we got all the scraped items, but we also received some statistics
on scope and duration of the scraping job.

However, we may want to have more fine-grained control over scraping to have
only single page scraped. To achieve this, we need to pass JSON payload to
ScrapyRT API. Let me show how this can be done through Python REPL:

```
$ python3
Python 3.9.12 (main, Mar 26 2022, 15:51:15)
[Clang 13.1.6 (clang-1316.0.21.2)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import requests
>>> api_url = 'http://localhost:9080/crawl.json'
>>> page_url = 'https://books.toscrape.com/catalogue/throwing-rocks-at-the-google-bus-how-growth-became-the-enemy-of-prosperity_948/index.html'
>>> payload = { 'request': { 'url': page_url, 'callback': 'parse_book_page' }, 'spider_name': 'books'}
>>> resp = requests.post(api_url, json=payload)
>>> resp
<Response [200]>
>>> from pprint import pprint
>>> pprint(resp.json())
{'items': [{'availability': '16',
            'description': 'Capital in the Twenty-First Century meets The '
                           'Second Machine Age in this stunning and optimistic '
                           'tour de force on the promise and peril of the '
                           'digital economy, from one of the most brilliant '
                           'social critics of our time. Digital technology was '
                           'supposed to usher in a new age of endless '
                           'prosperity, but so far it has been used to put '
                           'industrial capitalism on steroids, makin Capital '
                           'in the Twenty-First Century meets The Second '
                           'Machine Age in this stunning and optimistic tour '
                           'de force on the promise and peril of the digital '
                           'economy, from one of the most brilliant social '
                           'critics of our time. Digital technology was '
                           'supposed to usher in a new age of endless '
                           'prosperity, but so far it has been used to put '
                           'industrial capitalism on steroids, making it '
                           'harder for people and businesses to keep up. '
                           'Social networks surrender their original missions '
                           'to more immediately profitable data mining, while '
                           'brokerage houses abandon value investing for '
                           'algorithms that drain markets and our 401ks '
                           'alike--all tactics driven by the need to stoke '
                           'growth by any means necessary. Instead of taking '
                           'this opportunity to reprogram our economy for '
                           'sustainability, we have doubled down on growth as '
                           'its core command. We have reached the limits of '
                           'this approach. We must escape the growth trap, '
                           'once and for all.\xa0Media scholar and technology '
                           "author Douglas Rushkoff--one of today's most "
                           'original and influential thinkers--argues for a '
                           'new economic program that utilizes the unique '
                           'distributive power of the internet while breaking '
                           'free of the winner-take-all system the growth trap '
                           'leaves in its wake. Drawing on sources both '
                           'contemporary and historical, Rushkoff pioneers a '
                           'new understanding of the old economic paradigm, '
                           'from central currency to debt to corporations and '
                           'labor.Most importantly, he offers a series of '
                           'practical steps for businesses, consumers, '
                           'investors, and policymakers to remake the economic '
                           'operating system from the inside out--and prosper '
                           'along the way. Instead of boycotting Wal-Mart or '
                           'overtaxing the wealthy, we simply implement '
                           'strategies that foster the creation of value by '
                           'stakeholders other than just ourselves. From our '
                           'currency to our labor to the corporation, every '
                           'aspect of the economy can be reprogrammed with '
                           'minimal disruption to create a more equitably '
                           'distributed prosperity for all.Inspiring and '
                           'challenging, Throwing Rocks at the Google Bus '
                           'provides a pragmatic, optimistic, and '
                           'human-centered model for economic progress in the '
                           'digital age. ...more',
            'n_reviews': '0',
            'price_excl_tax': '31.12',
            'price_incl_tax': '31.12',
            'title': 'Throwing Rocks at the Google Bus: How Growth Became the '
                     'Enemy of Prosperity',
            'upc': '7858914fad68493c'}],
 'items_dropped': [],
 'spider_name': 'books',
 'stats': {'downloader/request_bytes': 565,
           'downloader/request_count': 2,
           'downloader/request_method_count/GET': 2,
           'downloader/response_bytes': 4883,
           'downloader/response_count': 2,
           'downloader/response_status_count/200': 1,
           'downloader/response_status_count/404': 1,
           'elapsed_time_seconds': 0.843302,
           'finish_reason': 'finished',
           'finish_time': '2022-06-04 09:12:00',
           'httpcompression/response_bytes': 22447,
           'httpcompression/response_count': 2,
           'item_scraped_count': 1,
           'log_count/DEBUG': 3,
           'log_count/INFO': 9,
           'memusage/max': 85594112,
           'memusage/startup': 85594112,
           'response_received_count': 2,
           'robotstxt/request_count': 1,
           'robotstxt/response_count': 1,
           'robotstxt/response_status_count/404': 1,
           'scheduler/dequeued': 1,
           'scheduler/dequeued/memory': 1,
           'scheduler/enqueued': 1,
           'scheduler/enqueued/memory': 1,
           'start_time': '2022-06-04 09:12:00'},
 'status': 'ok'}
```

As expected, we got a single item with scraped data from page we pointed at in
our request. Some of the arguments we previously passed as URL parameters
are now part of JSON payload. 

One thing we may want to do is to run ScrapyRT in Docker container
to expose Scrapy project through API. Zyte provides an official [ScrapyRT image](https://hub.docker.com/r/scrapinghub/scrapyrt)
that is unfortunately neglected and still uses Python 2.7 at the `latest` tag.
However, it is fairly simple to dockerize ScrapyRT without relying on it.
We can create the following Dockerfile at the same directory that 
has scrapy.cfg file:

```dockerfile
FROM python:3-slim

RUN pip3 install scrapy scrapyrt

RUN mkdir /books_to_scrape
ADD . /books_to_scrape
WORKDIR /books_to_scrape

EXPOSE 9080

ENTRYPOINT ["scrapyrt", "-i", "0.0.0.0"]
```

To learn more about ScrapyRT, see the [official documentation](https://scrapyrt.readthedocs.io/en/stable/).

Key limitatation to keep in mind is that ScrapyRT is not designed to support
long crawls. It is meant to be used to help software outside Scrapy to scrape
a single page or small number of pages. This solution effectively turns web
sites into RESTful APIs. However if you need a way to launch large scraping
jobs through REST API you should consider [Scrapyd](https://github.com/scrapy/scrapyd) 
API server that was designed to provide a way to manage scraping jobs from
outside Scrapy framework. To upload and run your Scrapy project in the
cloud you may want to consider either [Scrapy Cloud](https://www.zyte.com/scrapy-cloud/)
SaaS solution or [Scrapydweb](https://github.com/my8100/scrapydweb) for 
self-hosted option.

