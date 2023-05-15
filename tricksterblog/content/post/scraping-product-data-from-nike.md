+++
author = "rl1987"
title = "Scraping product data from Nike.com"
date = "2023-05-16"
draft = true
tags = ["scraping", "python", "scrapy", "sneakers"]
+++

Suppose you are looking to collect pricing data on male footwear from the
official website of one of the industry leaders - Nike.com. There's a 
[product list page](https://www.nike.com/w/mens-shoes-nik1zy7ok) that seems
like a good place to start, but the infinite scroll feature might seems puzzling
to budding web scraper developers. In this post we will go through developing 
a Scrapy project for scraping sneaker price data from this website. Some
familiarity with Scrapy and web scraping in general is assumed.

Before we proceed with writing the code, let us explore the site a little.
Open the source code of product list page and try searching for a product
title that we can see rendered on the page. The purpose of doing this is to
gain insight of how data is represented in the original HTML that is fetched
on the first load of the page. By searching for "Nike Air Max Pulse" we get 
some hits with this string being part of normal HTML, but more importantly
we get a hit in the big JSON document that is embedded in the page. We can see
that data on products (titles, prices, image URLs) is encoded into this JSON
string as well. 

[Screenshot 1](/2023-05-15_14.50.53.png)

By scrolling up, we find that the JSON string is wrapped in a script element 
(due to frontend programming reasons):

```html
<script id="__NEXT_DATA__" type="application/json">
```

[Screenshot 2](/2023-05-15_14.51.15.png)

This is good for us, as we can extract the data we need from big JSON string and
use it for our purposed. However, how does the infinite scroll work? How is the
new data loaded? This can be explored in Network tab of Chrome DevTools.

[Screenshot 3](/2023-05-15_14.58.45.png)
[Screenshot 4](/2023-05-15_14.59.29.png)

We can see that site launched an API call to api.nike.com every time new page of
product list data is needed (i.e. you scroll to the bottom and trigger the 
fetching of new data). The JSON response to this API request contains product
data (largely in the same structure as we found in the page source) and a section
for pagination that contains some relative URLs (starting with `/product_feed/rollup_threads/v2`)
that are passed into `endpoint` URL parameter when further pages of data are 
being loaded. The initial value for `endpoint` parameter that matches second
page of data can also be found in the big JSON in the page source:

```
"pageData":{"prev":"","next":"/product_feed/rollup_threads/v2?filter=marketplace%28US%29\u0026filter=language%28en%29\u0026filter=employeePrice%28true%29\u0026filter=attributeIds%2816633190-45e5-4830-a068-232ac7aea82c%2C0f64ecc7-d624-4e91-b171-b83a03dd8550%29\u0026anchor=24\u0026consumerChannelId=d9a5bc42-4b9c-4976-858a-f159cf99c647&count=24
```

[Screenshot 5](/2023-05-15_15.03.12.png)

This informs our general strategy for scraping:

1. Fetch the product list page HTML with nested JSON. Use it to extract some
initial product data and the first value for `endpoint` parameter to start API
scraping.
2. Scrape product feed API by traversing all pages. This gives product titles
and pricing info.
3. Augment data from step 2 by scraping product detail pages to add some more
data on products. 

Step 3 is technically not needed if we only want pricing information, but I'm
including it here as many web scraping project for ecommerce industry involve
scraping the PDP (product detail page) as well.

After new project boilerplate is generated with `scrapy startproject` and
`genspider` commands let us start by editing items.py to define a class for
an item (a unit of scraped data):

```python
# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NikeProductItem(scrapy.Item):
    title = scrapy.Field()
    subtitle = scrapy.Field()
    pid = scrapy.Field()
    current_price = scrapy.Field()
    empl_price = scrapy.Field()
    full_price = scrapy.Field()
    in_stock = scrapy.Field()
    product_url = scrapy.Field()
    image_urls = scrapy.Field()
    description = scrapy.Field()

```

The Scrapy spider class I generated is named `NikecomSpider` and resides in
nikecom.py file. Let's make this spider load the product list page and extract 
some initial product data:

```python
class NikecomSpider(scrapy.Spider):
    name = 'nikecom'
    allowed_domains = ['nike.com', 'www.nike.com', 'api.nike.com']
    start_urls = ['https://www.nike.com/w/mens-shoes-nik1zy7ok']

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse_first_page)

    def convert_product_dict_into_item(self, product):
        # Removed for brevity.

    def parse_first_page(self, response):
        next_data_json_str = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()

        json_dict = json.loads(next_data_json_str)
        props = json_dict.get("props")
        page_props = props.get("pageProps")
        initial_state = page_props.get("initialState")
        wall = initial_state.get("Wall")
        products = wall.get('products')

        for product in products:
            item = self.convert_product_dict_into_item(product)
            yield item
            # TODO: yield request to product page
```

I have created method `convert_product_dict_into_item()` that converts data from
original JSON to Scrapy item object, but for now this code is not shown for the
sake of brevity. Just keep in mind that it will be reused when we do API 
scraping.

Next thing we want to do in `parse_first_page()` method is to launch the first
API request. We do this based on initial `endpoint` parameter value that 
we extract from JSON string:

```python
        page_data = wall.get('pageData')
        if page_data is not None:
            next_page_link = page_data.get("next")
            if next_page_link is not None and next_page_link != '':
                yield self.create_feed_api_request(next_page_link)
```

Here we rely on another helper method to create the API request:

```python
    def create_feed_api_request(self, next_page_link):
        params = {
            'queryid': 'products',
            'anonymousId': '7CC266B713D36CCC7275B33B6E4F9206', #XXX
            'country': 'us',
            'endpoint': next_page_link,
            'language': 'en',
            'localizedRangeStr': '{lowestPrice} — {highestPrice}'
        }

        url = 'https://api.nike.com/cic/browse/v2'

        url = url + '?' + urlencode(params)

        return scrapy.Request(url, callback=self.parse_product_feed)
```

In `parse_product_feed()` method we process the API response, create item objects
and generate requests to product detail pages:

```python
    def parse_product_feed(self, response):
        json_str = response.text

        json_dict = json.loads(json_str)

        products = json_dict.get('data', dict()).get('products', dict()).get('products', [])

        for product in products:
            item = self.convert_product_dict_into_item(product)
            yield scrapy.Request(item['product_url'], meta={'item': item}, callback=self.parse_product_page)

        next_page_link = json_dict.get('data', dict()).get('products', dict()).get('pages', dict()).get('next')
        if next_page_link is not None and next_page_link != '':
            yield self.create_feed_api_request(next_page_link)
```

Note that partially-filled item object is passed to the next callback via the
`meta` dictionary. We modify the `parse_first_page()` method to do this as well,
instead of just generating item object.

In this sample project product detail page parsing is limited to extracting
only a couple of fields from the HTML:

```python
    def parse_product_page(self, response):
        item = response.meta.get('item')
        
        item['description'] = response.xpath('//div[contains(@class, "description-preview")]/p/text()').get()
        item['image_urls'] = response.xpath('//picture/source/@srcset').getall()

        yield item
```

This now generates the final item object, with product description and image 
URLs.

The final Scrapy spider code is as follows:

```python
import scrapy

import json
from urllib.parse import urlencode

from nike.items import NikeProductItem

class NikecomSpider(scrapy.Spider):
    name = 'nikecom'
    allowed_domains = ['nike.com', 'www.nike.com', 'api.nike.com']
    start_urls = ['https://www.nike.com/w/mens-shoes-nik1zy7ok']

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse_first_page)

    def convert_product_dict_into_item(self, product):
        item = NikeProductItem()
        
        item['title'] = product.get("title")
        item['subtitle'] = product.get("subtitle")
        item['pid'] = product.get("pid")
        
        price_dict = product.get("price", dict())
        if price_dict is not None:
            item['current_price'] = price_dict.get("currentPrice")
            item['empl_price'] = price_dict.get("employeePrice")
            item['full_price'] = price_dict.get("fullPrice")

        item['in_stock'] = product.get("inStock")
        item['product_url'] = product.get('url')
        if item['product_url'] is not None:
            item['product_url'] = item['product_url'].replace("{countryLang}", "https://www.nike.com")

        return item

    def create_feed_api_request(self, next_page_link):
        params = {
            'queryid': 'products',
            'anonymousId': '7CC266B713D36CCC7275B33B6E4F9206', #XXX
            'country': 'us',
            'endpoint': next_page_link,
            'language': 'en',
            'localizedRangeStr': '{lowestPrice} — {highestPrice}'
        }

        url = 'https://api.nike.com/cic/browse/v2'

        url = url + '?' + urlencode(params)

        return scrapy.Request(url, callback=self.parse_product_feed)

    def parse_first_page(self, response):
        next_data_json_str = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()

        json_dict = json.loads(next_data_json_str)
        props = json_dict.get("props")
        page_props = props.get("pageProps")
        initial_state = page_props.get("initialState")
        wall = initial_state.get("Wall")
        products = wall.get('products')

        for product in products:
            item = self.convert_product_dict_into_item(product)
            if item.get('product_url') is not None:
                yield scrapy.Request(item['product_url'], meta={'item': item}, callback=self.parse_product_page)

        page_data = wall.get('pageData')
        if page_data is not None:
            next_page_link = page_data.get("next")
            if next_page_link is not None and next_page_link != '':
                yield self.create_feed_api_request(next_page_link)

    def parse_product_page(self, response):
        item = response.meta.get('item')
        
        item['description'] = response.xpath('//div[contains(@class, "description-preview")]/p/text()').get()
        item['image_urls'] = response.xpath('//picture/source/@srcset').getall()

        yield item

    def parse_product_feed(self, response):
        json_str = response.text

        json_dict = json.loads(json_str)

        products = json_dict.get('data', dict()).get('products', dict()).get('products', [])

        for product in products:
            item = self.convert_product_dict_into_item(product)
            yield scrapy.Request(item['product_url'], meta={'item': item}, callback=self.parse_product_page)

        next_page_link = json_dict.get('data', dict()).get('products', dict()).get('pages', dict()).get('next')
        if next_page_link is not None and next_page_link != '':
            yield self.create_feed_api_request(next_page_link)


```

Running this requires no proxies or anything to deal with antibots despite
Nike being a customer of not one, but two antibot solutions - Kasada and Akamai
Bot Manager. This provides an interesting example of how there are multiple levels
to protection against automation. Automatically creating Nike accounts and/or
placing orders is known to be challenging thing to do, yet Nike allows a simple
form of product data scraping without imposing any difficulty on doing that.
What we developed here was a quite simple Scrapy project that was based on 
some quite basic forms of reverse engineering. 


