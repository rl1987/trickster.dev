+++
author = "rl1987"
title = "Scrapy framework architecture"
date = "2022-03-21"
draft = true
tags = ["web-scraping", "python", "scrapy"]
+++

In this post we will take a deeper look into architecture of not just Scrapy projects, but
Scrapy framework itself. We will go through some key components of Scrapy and will look into
how data is flowing through the system.

Let us look into the following picture from Scrapy documentation:
https://docs.scrapy.org/en/latest/_images/scrapy_architecture_02.png

We see the following components:

* Engine that is the central switchboard for all data that is transferred inside Scrapy when it is running.
* Spiders that traverse links and parse data to generate new requests and items (units of
scraped data).
* Spider middlewares (between spiders and Engine) to customise spider functionality by hooking into requests, responses
and error conditions. Some default spider middlewares are integrated into each new Scrapy project and deal with things
like filling `Referer` header, tracking crawling depth, filtering out unsuccessful responses, filtering out requests
to outside the domain of site being scraped.
* Downloader is where actual HTTP requests are made and responses are received. 
* Downloader middlewares (between Engine and Downloader) can be implemented for for lower-level customisation of requests
and responses. It can also override some requests with a response that was prepared beforehand. Default downloader
middlewares deal with cookie management, HTTP headers, timeouts, retries, caching, heeding robots.txt rules and some other
aspects of HTTP protocol.
* Scheduler keeps track of requests to be made (in a priority queue) and when requested gives one to the Engine.
* Item pipelines can be implemented for post-processing of scraped data, such as cleaning, reformatting and exporting to
external stores.
* Optionally, there can be Extensions which are Python classes that implement further customisations to Scrapy.

Out of these, one or more spiders are implemented in each Scrapy project. Depending on specifics of the project, you may
also need to implement one or more of spider/downloader middlewares and item pipelines. You are unlikely to deal with
Extension development unless you work with deep customisation of Scrapy framework.

Now let us go through data flow in the picture.

1. Spider is launched and generates some initial requests. They are passed into Engine through zero or more spider middlewares.
Each spider middleware is given opportunity to modify or drop any of the requests.
2. Engine passes requests into Scheduler, which puts them into a queue.
3. Engine asks Scheduler for next request to be processed. Scheduler gives it to Engine (as long as queue is not empty; if it is,
scraping job is finished).
4. Engine sends the request to Downloader through a sequence of one or more downloader middlewares. Like spider middlewares,
each of the downloader middlewares are given opportunity to modify or drop the request.
5. Downloader performs HTTP request and generates response object. It is returned through donwloader middleware to engine.
Like with the request, they can drop or modify the response.
6. Engine sends the response through spider middlewares to the spider. 
7. Spider parses the response and generates zero or more items and zero or more new requests. These are sent to Engine 
via spider middlewares.
8. Engine sends items to item pipelines and requests to scheduler. At this point, the process loops back to step 3 and is
repeated until there are no new requests to be processed.

Note that despite Scrapy being able to launch multiple requests concurrently, no multithreading is used anywhere is Scrapy.
Instead, asynchronous network event handling is done through Twisted network programming framework. This has some ramifications
for web scraper developers as well. First, we should avoid doing things that block unless they are really quick and/or rare
as otherwise they would slow down the entire system (as could be seen by trying to use openpyxl in a pipeline to export very large
amounts of data). Second, we have to take care to use `yield` (not `return`) keyword 
when new items/requests are being created in the spider, as that allows deferring the entire code path until the moment the 
result is needed.
