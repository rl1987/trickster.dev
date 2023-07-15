+++
author = "rl1987"
title = "Using Scrapy-playwright for integrating browser automation with Scrapy"
date = "2023-07-31"
tags = ["scraping", "scrapy", "playwright"]
draft = true
+++

Scrapy framework provides a great deal of machinery for developing and operating
web scrapers that is based on launching requests and parsing responses. However,
sometimes it is desirable to introduce browser automation into a web scraping
project. One may want to have code as general as possible across many target
sites, evade certain kinds of blocking (e.g. Javascript challenges) or simply 
take screenshots of pages being scraped. [Scrapy-playwright](https://github.com/scrapy-plugins/scrapy-playwright) 
is Scrapy plugin that connects Scrapy with MS Playwright browser automation
software. In this post we will get familiar with it and go through some code
examples that demonstrate the integration between the two.

