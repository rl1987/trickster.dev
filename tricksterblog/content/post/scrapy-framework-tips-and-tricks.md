+++
author = "rl1987"
title = "Scrapy framework tips and tricks"
date = "2022-02-20"
draft = true
tags = ["web-scraping", "python", "scrapy"]
+++

Use Scrapy shell for interactive experimentation
------------------------------------------------

Running `scrapy shell` gives you an interactive environment for experimentation with how your
code interacts with the site being scraped. For example, running `fetch()` with URL of page
fetches the page and creates a `response` variable with `scrapy.Response` object for that page.
`view(response)` opens the browser to let you see the HTML that the Scrapy spider would fetch.
This bypasses some of the client-side rendering and also lets us detect if the site has some
countermeasures against scraping.

Furthermore, calling `css()` or `xpath()` methods on response object is a convenient way to
refine your CSS or XPath queries before putting them into actual Python code.

To learn more about Scrapy shell, see: https://docs.scrapy.org/en/latest/topics/shell.html

Use image/file pipeline for file downloading
--------------------------------------------

Sometimes your web scraping project will involve downloading images or files in general.
Scrapy provides some official pipelines for this exact task.

To download any kind of files, we can integrate `FilesPipeline` by adding
it into `ITEM_PIPELINES` map in settings.py file like this:

```python
ITEM_PIPELINES = {'scrapy.pipelines.files.FilesPipeline': 1}
```

You would also need to set the directory path for files to be downloaded:

```python
FILES_STORE = '/path/to/valid/dir'
```

Furthermore, your items will need to include `file_urls` field with a list of file URLs.
When files pipeline processes the item, it will download each file into directory you
have configured and will set a `files` property with dictionary of original URL and
path of downloaded file. To convert file URL into file name, SHA1 hash is computed on
URL and prepended to the original file extension.

Integration of images pipeline is rather similar. You would edit settings.py to add
`scrapy.pipelines.files.FilesPipeline` into `ITEM_PIPELINES` dictionary and set
`IMAGES_STORE` to path of directory that will be used for storing files. However,
images pipeline provides some image processing capabilities, thus requiring that
[Pillow](https://pillow.readthedocs.io/en/stable/) module is installed. By default,
images pipeline automatically converts all downloaded images to JPEG format.

Both pipelines allow storing downloaded files on stores external to local file system:

* AWS S3 buckets
* Remote FTP servers
* Google Cloud storage buckets

To learn more about this, see: https://docs.scrapy.org/en/latest/topics/media-pipeline.html

Use automatic throttling for scraping rate-limited sites
--------------------------------------------------------

Some sites implement rate-limiting and will refuse to give you responses with proper pages
if you are generating too many requests too quickly from single IP. A simple way to slow
down your Scrapy project is to decrease the following values in settings.py:

* `CONCURRENT_REQUESTS_PER_DOMAIN`
* `CONCURRENT_REQUESTS_PER_IP`

These variables control upper limit of how many concurrent requests spider is allowed to
launch per domain/target IP address - only one of them should be set.

A more advanced way to slow down is to use `AutoThrottle` extension by uncommenting parts
and experimenting with values to reach a point of no requests being dropped:

```python
# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False
```

This will enable an adaptive throttling algorithm that will take into account a load of
both your Scrapy instance and remote server(s) being scraped.

To learn more about automatic throttling, see: https://docs.scrapy.org/en/latest/topics/autothrottle.html

Deploy Scrapy projects to the cloud
-----------------------------------

Once you have your Scrapy project running properly, you may want to avoid running it on your local machine to
perform scraping. There are several ways to get it running in the cloud environment.

The simplest way is to get a cheap VPS (e.g. $5/month Digital Ocean droplet), install Scrapy there, upload your
Scrapy project via SFTP and run it in tmux session.

Another way is to self-host a solution like [Scrapydweb](https://github.com/my8100/scrapydweb) that will provide
you with web interface to upload your Scrapy project and monitor scraping progress on the dashboard.

Yet another way is to sign up for [Scrapy Cloud](https://www.zyte.com/scrapy-cloud/) - the official service from
creators of Scrapy. This service has it's own CLI tool for uploading your Scrapy project and launching it in the 
cloud environment, which means you can integrate it into your CI/CD pipeline. 

Use Item Loader to streamline item creation
-------------------------------------------

Scrapy lets you create Item Loaders to simplify and streamline item creation based on CSS selectors and XPath 
queries. Furthermore, it allows you to include extra steps such as whitespace stripping and other parsing tasks.

Scrapy documentation provides the following example on how Item Loader could be used in the spider:

```python
from scrapy.loader import ItemLoader
from myproject.items import Product

def parse(self, response):
    l = ItemLoader(item=Product(), response=response)
    l.add_xpath('name', '//div[@class="product_name"]')
    l.add_xpath('name', '//div[@class="product_title"]')
    l.add_xpath('price', '//p[@id="price"]')
    l.add_css('stock', 'p#stock]')
    l.add_value('last_updated', 'today') # you can also use literal values
    return l.load_item()
```

To learn more about Item Loaders, see: https://docs.scrapy.org/en/latest/topics/loaders.html

