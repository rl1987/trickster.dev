+++
author = "rl1987"
title = "Retrospective scraping of historical data from Internet Archive snapshots"
date = "2023-11-15"
draft = true
tags = ["scraping", "osint", "python"]
+++

Some internet research activities are based on not only present data, but also
on accessing historical data that was posted online. We will go through a simple 
example of how scraping pre-crawled pages from Internet Archive Wayback
Machine can be used to gather historical data for data science purposes. We will
be scraping historical snapshots of Iowa Department of Corrections [inmate 
statistics page](https://doc-search.iowa.gov/dailystatistics) to create a 
temporal inmate population dataset and draw some graphs. Data we want to collect
is in "Current Count" and "Instution" columns of the table. For scraping we will
use Python with requests and lxml modules. For dataviz we will use Pandas and 
Matplotlib.

WRITEME
