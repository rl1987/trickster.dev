+++
author = "rl1987"
title = "Using Scrapy-playwright for integrating browser automation with Scrapy"
date = "2023-07-22"
tags = ["scraping", "scrapy", "playwright"]
+++

Scrapy framework provides a great deal of machinery for developing and operating
web scrapers that is based on launching requests and parsing responses. However,
sometimes it is desirable to introduce browser automation into a web scraping
project. One may want to have code as general as possible across many target
sites, address certain kinds of blocking (e.g. Javascript challenges) or simply 
take screenshots of pages being scraped. [Scrapy-playwright](https://github.com/scrapy-plugins/scrapy-playwright) 
is Scrapy plugin that connects Scrapy with MS Playwright browser automation
software. In this post we will get familiar with it and go through some code
examples that demonstrate the integration between the two.

The following steps require Scrapy, Playwright and Scrapy-playwright to be 
installed in your system.

To enable Scrapy-playwright in the Scrapy project, we have to override
the [`DOWNLOADER_HANDLERS`](https://docs.scrapy.org/en/latest/topics/settings.html#std-setting-DOWNLOAD_HANDLERS) 
configuration parameter to the following:

```python
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
```

Furthermore, we must also override [`TWISTED_REACTOR`](https://docs.scrapy.org/en/latest/topics/settings.html?highlight=TWISTED_REACTOR#twisted-reactor):

```python
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
```

This replaces a class for reactor object class that is used by Scrapy. Reactor
object is where network event loop is running for the purposes of Twisted
network programming framework that Scrapy is based upon. 

Now we can use Playwright integration for launching some or all of the requests 
through the browser. If we want the request to be performed through browser,
we add `"playwright": True` to the `meta` dictionary for that request.

Let us go through a simple example of Scrapy-based script that relies on
Playwright to achieve greater scraper generality when checking for presence
of user-provided keyword on the pages.

Take a look at this code:

```python
#!/usr/bin/python3

import argparse
from datetime import datetime
import sys
import os
from urllib.parse import urlparse
import logging

import scrapy
from scrapy.crawler import CrawlerProcess


class KeywordSpider(scrapy.Spider):
    name = "kwchecker"
    start_urls = []
    allowed_domains = []
    keywords = []
    use_playwright = False

    def __init__(self, start_urls, keywords, use_playwright, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = list(set(start_urls))

        allowed_domains = []
        for start_url in self.start_urls:
            domain = urlparse(start_url).netloc
            allowed_domains.append(domain)

        self.allowed_domains = list(set(allowed_domains))
        self.keywords = list(set(keywords))
        self.use_playwright = use_playwright

    def start_requests(self):
        meta = {"playwright": self.use_playwright}
        for start_url in self.start_urls:
            yield scrapy.Request(start_url, meta=meta)

    def parse(self, response):
        meta = dict()
        if response.meta.get("playwright") is not None:
            meta["playwright"] = response.meta.get("playwright")
        try:
            text = " ".join(response.xpath("*//text()").getall()).strip()
        except:
            return

        for keyword in self.keywords:
            if keyword.lower() in text.lower():
                yield {
                    "keyword": keyword,
                    "url": response.url,
                    "seen_at": datetime.now().isoformat(),
                }

        links = response.xpath("//a/@href").getall()
        for link in links:
            o = urlparse(link)
            if o.scheme == "" or o.scheme == "http" or o.scheme == "https":
                yield response.follow(link, meta=meta)


def read_lines(file_path):
    in_f = open(file_path, "r")
    lines = in_f.read().strip().split("\n")
    in_f.close()

    lines = list(map(lambda line: line.strip(), lines))
    lines = list(set(lines))

    return lines


def main():
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--start-urls",
        required=False,
        help="List of start URLs, one per line",
        default="start_urls.txt",
    )
    parser.add_argument(
        "--keywords",
        required=False,
        help="List of keywords, one per line",
        default="keywords.txt",
    )
    parser.add_argument(
        "--use-playwright",
        required=False,
        help="Use Playwright",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "--output-csv-file",
        required=False,
        help="Output CSV file",
        default="output.csv",
    )

    parsed_args = vars(parser.parse_args(sys.argv[1:]))
    print("Parsed CLI args: {}".format(parsed_args))

    start_urls = read_lines(parsed_args.get("start_urls"))
    keywords = read_lines(parsed_args.get("keywords"))
    output_csv_file = parsed_args.get("output_csv_file")
    use_playwright = parsed_args.get("use_playwright")

    if os.path.isfile(output_csv_file):
        os.unlink(output_csv_file)

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "sec-ch-ua": '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    }

    settings = {
        "USER_AGENT": headers.get("user-agent"),
        "DEFAULT_REQUEST_HEADERS": headers,
        "FEEDS": {output_csv_file: {"format": "csv"}},
        "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
    }

    if use_playwright:
        settings["DOWNLOAD_HANDLERS"] = {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        }

        settings[
            "TWISTED_REACTOR"
        ] = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

    process = CrawlerProcess(settings=settings)

    process.crawl(KeywordSpider, start_urls, keywords, use_playwright)
    process.start()


if __name__ == "__main__":
    main()
```

For the sake of simplicity, we use [`CrawlerProcess`](https://docs.scrapy.org/en/latest/topics/practices.html?highlight=CrawlerProcess#run-scrapy-from-a-script)
to run a single Scrapy spider for a script instead of creating a Scrapy project
that has far more boilerplate. We override the aforementioned settings, as
well as `USER_AGENT` and `DEFAULT_REQUEST_HEADERS` to make our scraper look
more like a normal browser. Note that the user of this script is allowed to
choose not to use browser automation by not passing in `--use-playwright`
CLI option. Scrapy spider works pretty much the same, except that value for
`playwright` key in `meta` dictionary is set to `False`.

When running this script we can see some output that is a little different
than what we regulary see from Scrapy:

```
$ kw_checker.py --use-playwright --start-urls start_urls.txt --keywords keywords.txt --output-csv-file results.csv
Parsed CLI args: {'start_urls': 'start_urls.txt', 'keywords': 'keywords.txt', 'use_playwright': True, 'output_csv_file': 'results.csv'}
2023-07-21 16:26:09 [scrapy.utils.log] INFO: Scrapy 2.8.0 started (bot: scrapybot)
2023-07-21 16:26:09 [scrapy.utils.log] INFO: Versions: lxml 4.9.2.0, libxml2 2.9.13, cssselect 1.2.0, parsel 1.7.0, w3lib 2.1.1, Twisted 22.10.0, Python 3.11.4 (main, Jun 20 2023, 17:23:00) [Clang 14.0.3 (clang-1403.0.22.14.1)], pyOpenSSL 23.1.1 (OpenSSL 3.1.0 14 Mar 2023), cryptography 40.0.1, Platform macOS-13.3.1-arm64-arm-64bit
2023-07-21 16:26:09 [scrapy.crawler] INFO: Overridden settings:
{'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7',
 'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
 'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
               'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 '
               'Safari/537.36'}
2023-07-21 16:26:09 [asyncio] DEBUG: Using selector: KqueueSelector
2023-07-21 16:26:09 [scrapy.utils.log] DEBUG: Using reactor: twisted.internet.asyncioreactor.AsyncioSelectorReactor
2023-07-21 16:26:09 [scrapy.utils.log] DEBUG: Using asyncio event loop: asyncio.unix_events._UnixSelectorEventLoop
2023-07-21 16:26:09 [scrapy.extensions.telnet] INFO: Telnet Password: 8ed078a7779ff379
2023-07-21 16:26:09 [scrapy.middleware] INFO: Enabled extensions:
['scrapy.extensions.corestats.CoreStats',
 'scrapy.extensions.telnet.TelnetConsole',
 'scrapy.extensions.memusage.MemoryUsage',
 'scrapy.extensions.feedexport.FeedExporter',
 'scrapy.extensions.logstats.LogStats']
2023-07-21 16:26:10 [scrapy.middleware] INFO: Enabled downloader middlewares:
['scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware',
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
2023-07-21 16:26:10 [scrapy.middleware] INFO: Enabled spider middlewares:
['scrapy.spidermiddlewares.httperror.HttpErrorMiddleware',
 'scrapy.spidermiddlewares.offsite.OffsiteMiddleware',
 'scrapy.spidermiddlewares.referer.RefererMiddleware',
 'scrapy.spidermiddlewares.urllength.UrlLengthMiddleware',
 'scrapy.spidermiddlewares.depth.DepthMiddleware']
2023-07-21 16:26:10 [scrapy.middleware] INFO: Enabled item pipelines:
[]
2023-07-21 16:26:10 [scrapy.core.engine] INFO: Spider opened
2023-07-21 16:26:10 [scrapy.extensions.logstats] INFO: Crawled 0 pages (at 0 pages/min), scraped 0 items (at 0 items/min)
2023-07-21 16:26:10 [scrapy.extensions.telnet] INFO: Telnet console listening on 127.0.0.1:6023
2023-07-21 16:26:10 [scrapy-playwright] INFO: Starting download handler
2023-07-21 16:26:10 [scrapy-playwright] INFO: Starting download handler
2023-07-21 16:26:15 [scrapy-playwright] INFO: Launching browser chromium
2023-07-21 16:26:15 [scrapy-playwright] INFO: Browser chromium launched
2023-07-21 16:26:15 [scrapy-playwright] DEBUG: Browser context started: 'default' (persistent=False)
2023-07-21 16:26:15 [scrapy-playwright] DEBUG: [Context=default] New page created, page count is 1 (1 for all contexts)
2023-07-21 16:26:15 [scrapy-playwright] DEBUG: [Context=default] New page created, page count is 2 (2 for all contexts)
2023-07-21 16:26:15 [scrapy-playwright] DEBUG: [Context=default] Request: <GET http://quotes.toscrape.com/js/> (resource type: document, referrer: None)
2023-07-21 16:26:15 [scrapy-playwright] DEBUG: [Context=default] Request: <GET http://books.toscrape.com/> (resource type: document, referrer: None)
2023-07-21 16:26:16 [scrapy-playwright] DEBUG: [Context=default] Response: <200 http://books.toscrape.com/> (referrer: None)
2023-07-21 16:26:16 [scrapy-playwright] DEBUG: [Context=default] Response: <200 http://quotes.toscrape.com/js/> (referrer: None)
2023-07-21 16:26:16 [scrapy-playwright] DEBUG: [Context=default] Request: <GET http://books.toscrape.com/static/oscar/css/styles.css> (resource type: stylesheet, referrer: http://books.toscrape.com/)
2023-07-21 16:26:16 [scrapy-playwright] DEBUG: [Context=default] Request: <GET http://books.toscrape.com/static/oscar/js/bootstrap-datetimepicker/bootstrap-datetimepicker.css> (resource type: stylesheet, referrer: http://books.toscrape.com/)
2023-07-21 16:26:16 [scrapy-playwright] DEBUG: [Context=default] Request: <GET http://books.toscrape.com/static/oscar/css/datetimepicker.css> (resource type: stylesheet, referrer: http://books.toscrape.com/)
2023-07-21 16:26:16 [scrapy-playwright] DEBUG: [Context=default] Request: <GET http://quotes.toscrape.com/static/bootstrap.min.css> (resource type: stylesheet, referrer: http://quotes.toscrape.com/js/)
2023-07-21 16:26:16 [scrapy-playwright] DEBUG: [Context=default] Request: <GET http://quotes.toscrape.com/static/main.css> (resource type: stylesheet, referrer: http://quotes.toscrape.com/js/)
2023-07-21 16:26:16 [scrapy-playwright] DEBUG: [Context=default] Request: <GET http://quotes.toscrape.com/static/jquery.js> (resource type: script, referrer: http://quotes.toscrape.com/js/)
```

We see that a headless Chromium browser is launched and that a browser
context is being mentioned. A browser context is essentially a session within
a browser that is controlled by Playwright.

As we would expect, images and JavaScript files are downloaded by the 
browser without spider explicitly asking for that:

```
2023-07-21 16:32:53 [scrapy-playwright] DEBUG: [Context=default] Response: <200 http://books.toscrape.com/static/oscar/js/bootstrap-datetimepicker/locales/bootstrap-datetimepicker.all.js> (referrer: None)
2023-07-21 16:32:53 [scrapy-playwright] DEBUG: [Context=default] Response: <200 http://books.toscrape.com/media/cache/ee/a9/eea9e831f8964b4dc0190c84a1f9a1f6.jpg> (referrer: None)
2023-07-21 16:32:53 [scrapy-playwright] DEBUG: [Context=default] Response: <200 http://books.toscrape.com/media/cache/dc/4d/dc4d070e33813a07a4e02f069e6d482f.jpg> (referrer: None)
```


