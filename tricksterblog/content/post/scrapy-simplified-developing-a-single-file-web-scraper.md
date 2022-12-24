+++
author = "rl1987"
title = "Scrapy simplified: developing a single file web scraper"
date = "2022-12-24"
draft = true
tags = ["web-scraping", "scrapy", "python"]
+++

The default way of using Scrapy entails running `scrapy startproject` to generate
a bunch of starter code across multiple files. For small scale scrapers
that's a bit of overkill. It's far simpler to have a single Python script file that
you can run when you want to scrape some data. The `CrawlerProcess` class in Scrapy
framework enables us to develop such a script.

For the sake of example, let us suppose we are interested in extracting some basic 
information about Fortune 500 companies from the Fortune 500 website. To do a little
exploration and planning, let us load the 
[Fortune 500 search page](https://fortune.com/ranking/fortune500/2022/search/)
via Scrapy shell:

```
$ scrapy view "https://fortune.com/ranking/fortune500/2022/search/"
```

This opens up a browser window with HTML as the Scrapy was able to fetch it.
Luckily we did not run into any countermeasures against scraping. If we view
the page source we find that all the info being rendered in the table is 
available in JSON format inside `<script>` with `id` equal to `__NEXT_DATA__`.
This JSON string is the biggest thing in the HTML that Scrapy fetched. 
So that's what we're going to scrape to get links to company pages.

Let us look into a company profile page.

```
$ scrapy view "https://fortune.com/company/verizon/fortune500/"
```

Once again, we find the same kind of script tag from Next.js framework
that we can extract data from.

TODO: screenshots

Let us go through the following example scraper. 

```python
#!/usr/bin/python3

import json

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector

class F500Spider(scrapy.Spider):
    start_urls = ["https://fortune.com/ranking/fortune500/2022/search/"]
    name = "f500"

    def start_requests(self):
        yield scrapy.Request(self.start_urls[0], callback=self.parse_search)

    def parse_search(self, response):
        json_str = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
        json_dict = json.loads(json_str)

        item_dicts = (
            json_dict.get("props", dict())
            .get("pageProps", dict())
            .get("franchiseList", dict())
            .get("items", [])
        )

        for item_dict in item_dicts:
            slug = item_dict.get("slug")
            rank = item_dict.get("data", dict()).get("Rank", "").replace(",", "")
            rank = int(rank)

            if slug is not None and rank <= 500:
                yield response.follow(slug, callback=self.parse_company_page)

    # TODO: make it scrape this as well: https://fortune.com/company/amphenol/fortune500/
    def parse_company_page(self, response):
        json_str = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
        try:
            json_dict = json.loads(json_str)
        except:
            return
        
        fli = json_dict.get("props", dict()).get("pageProps", dict()).get("franchiseListItem")
        if fli is None:
            return

        company_name = fli.get("title")
        rank = fli.get("rank")

        company_info = fli.get("companyInfo", dict())

        website = company_info.get("Website")
        if website is not None and website.startswith("<a"):
            website = Selector(text=website).xpath('//a/text()').get()
    
        country = company_info.get("Country")
        industry = company_info.get("Industry")
        ticker = company_info.get("Ticker")

        yield {
            "rank": rank,
            "company_name": company_name,
            "website": website,
            "country": country,
            "industry": industry,
            "ticker": ticker
        }


def main():
    # See: https://docs.scrapy.org/en/latest/topics/practices.html#run-from-script
    process = CrawlerProcess(settings={
        "FEEDS": {
            "f500.csv": {"format": "csv"}
        }
    })
    process.crawl(F500Spider)
    process.start()


if __name__ == "__main__":
    main()

```

The key part is the spider that we develop by creating a subclass of `scrapy.Spider`,
the same way we would be doing in spiders/ directory of regular Scrapy project.
To launch the spider without the entire shebang that would come with Scrapy project we
need to instantiate a `scrapy.crawler.CrawlerProcess` object with settings dictionary,
call the `crawl()` method with our spider class and the call the `start()` method.
This will make the spider run until completion. Script will finish running once the 
scraping is done.

