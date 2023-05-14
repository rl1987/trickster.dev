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
string as well. By scrolling up, we find that the JSON string is wrapped in
a script element (due to frontend programming reasons):

```html
<script id="__NEXT_DATA__" type="application/json">
```

This is good for us, as we can extract the data we need from big JSON string and
use it for our purposed. However, how does the infinite scroll work? How is the
new data loaded? This can be explored in Network tab of Chrome DevTools.

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




