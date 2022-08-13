+++
author = "rl1987"
title = "Writing custom Scrapy middleware for proxy pool integration"
date = "2022-08-19"
draft = true
tags = ["scraping", "anti-bot", "scrapy", "proxies"]
+++

One needs to use proxy pool to scrape some of the sites that implement countermeasures
against scraping. It might be because of IP-based rate limiting, geographic restrictions,
AS-level traffic filtering or even something more advanced such as TLS fingerprinting.
When Scrapy framework is used to implement a scraper, there are multiple
ways to do so, depending on the exact situation:

* Setting `HTTPS_PROXY` environment variable when running a spider will make the traffic
go through the proxy. Note that this will also apply to requests being made not only from
spider, but from pipelines and other parts of the project, which may not be desirable.
* Setting proxy URL at `proxy` key of the `meta` dictionary for each request. This allows
us to be flexible on which requests are being sent through a proxy, but makes code less 
clean by moving the proxy integration into spider class.

Both of these options depend on the standard HTTP proxy middleware that is available
in a vanilla Scrapy project.

However we may want to have more flexibility and introduce additional logic regarding
how exactly are the requests routed through a proxy pool. This can be done through 
implementing an additional downloaded middleware that will augment
[`HttpProxyMiddleware`](https://docs.scrapy.org/en/latest/topics/downloader-middleware.html?highlight=HttpProxyMiddleware#module-scrapy.downloadermiddlewares.httpproxy)
by assigning a proxy URL to some or all of the requests. To do so, we edit middlewares.py
file in a Scrapy project and create a downloader middleware class there.
To process each HTTP request (represented by `scrapy.Request` object) we must
implement our own [`process_request()`](https://docs.scrapy.org/en/latest/topics/downloader-middleware.html?highlight=HttpProxyMiddleware#scrapy.downloadermiddlewares.DownloaderMiddleware.process_request) method. If we need to assign a proxy URL to request, we put it into `meta` dictionary
at `proxy` key. If not, we leave it as-is. Either way we don't need to return anything
from this method.

For example, we may want to integrate BrightData proxy pool in a way that forces exit IP
randomisation. The following code implements a simple downloader middleware that
takes BrightData zone credentials from settings, appends session ID to the user name,
generates proxy URL and puts it into `meta` dictionary:

```python
from museums.settings import (
    BRIGHT_DATA_ENABLED,
    BRIGHT_DATA_ZONE_USERNAME,
    BRIGHT_DATA_ZONE_PASSWORD,
)

from w3lib.http import basic_auth_header

import random


class BrightDataDownloaderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def process_request(self, request, spider):
        if not BRIGHT_DATA_ENABLED:
            return None

        request.meta["proxy"] = "http://zproxy.lum-superproxy.io:22225"

        username = BRIGHT_DATA_ZONE_USERNAME + "-session-" + str(random.random())

        request.headers["Proxy-Authorization"] = basic_auth_header(
            username, BRIGHT_DATA_ZONE_PASSWORD
        )


```

It also sets a `Proxy-Authorization` in a way that it is used for HTTP Basic Auth.

To use this middleware in the Scrapy project, we must not only set the configuration variables,
but also edit `DOWNLOADER_MIDDLEWARES` to activate this middleware with a priority value:

```python
# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'museums.middlewares.BrightDataDownloaderMiddleware': 500,
}
```

If this does not work you may want to check that priority of your custom middleware is higher
(numerically lower) than that of `HttpProxyMiddleware`, as we need to set proxy URL and 
credentials before it gets to the regular middlware.

For further examples on Scrapy middlewares that integrate with proxy pools you may
want to read the code of the following projects:

* [scrapy-zyte-smartproxy](https://github.com/scrapy-plugins/scrapy-zyte-smartproxy) - official
middleware for the Zyte Smart Proxy service. Implements some reliability and error handling
features such as exponential backoff and gracefully handling an outage of proxy pool, as well
as managing vendor-specific HTTP headers.
* [scrapy-rotating-proxies](https://github.com/TeamHG-Memex/scrapy-rotating-proxies) - two
middlewares that autorotate proxies for you with some ban detection logic. Lets you customise
the ban detection policy.

