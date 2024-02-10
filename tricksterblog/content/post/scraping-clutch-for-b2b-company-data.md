+++
author = "rl1987"
title = "Scraping Clutch for B2B company data"
date = "2024-02-15"
draft = true
tags = ["python", "web-scraping"]
+++

[Clutch.co](https://clutch.co/) is a web portal serving as B2B service company
directory. One may want to scrape it to make a list of companies within a
service niche to target them with some form of outreach. But the thing is, 
Clutch is fighting scraping attempt by using Cloudflare antibot service - 
naively fetching a page from this site gives us a 403 response with JS challenge.
So what do we do?
