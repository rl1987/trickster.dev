+++
author = "rl1987"
title = "Abusing GOAT mobile API for scraping and automation"
date = "2023-08-14"
draft = true
tags = ["scraping", "automation"]
+++

GOAT is an online platform for retail sale and reselling of certain consumer
products - primarily sneakers, apparel and electronics. It is estimated to 
have about 50 million active users that include some one million sellers. When
there's a major userbase, there's a potential to extract monetary benefit by
scraping the data and/or running some automations. But 1661 Inc., a company that
is developing GOAT don't want us to do that. GOAT is one of the websites that 
proactively fight automated traffic. For example, merely trying load the front 
page in Scrapy shell gives us a Cloudflare error.

[TODO: screenshot]

So we have to proceed differently. One trick from grayhat automation arsenal is
to MITM mobile app traffic to work out the exact API calls being done against 
the backend system, then to reproduce it programmatically. One example will be
a simple API scraping to extract data. Another will be demonstrating how mobile
API can be abused to automate user actions.



