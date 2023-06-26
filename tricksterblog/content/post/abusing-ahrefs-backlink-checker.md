+++
author = "rl1987"
title = "Abusing Ahrefs Backlink Checker"
date = "2023-06-26"
tags = ["scraping"]
draft = true
+++

World Wide Web is a network of HTML documents (pages) with hyperlinks between 
them. Consider a directed graph that consist of vertices representing pages
and edges representing links between pages. For a given page, links from other
pages to that page are known as backlinks. Backlinks are of significance to 
search engine ranking of the site. Furthermore, OSINT practitioners and web
scraper developers may want to find sites/pages linking to certain pages/files
on the web as it would help traversing the data landscape. Major SEO SaaS apps
(Ahrefs, SEMRush, Moz, etc.) are sourcing their data via large-scale web
crawling operations that build up a fairly complete maps of the web and thus 
can be leveraged for this purpose. In this post we will go through an example 
of abusing a free [Ahrefs Backlink Checker](https://ahrefs.com/backlink-checker) 
to show how a SEO tool can be abused to scrape a list of backlinks.



WRITEME: exploration of API flow

WRITEME: process of getting the API request right

WRITEME: the final script and sample of output data

