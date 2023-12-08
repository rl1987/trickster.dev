+++
author = "rl1987"
title = "Retrospective scraping of historical data from Internet Archive snapshots"
date = "2023-12-31"
draft = true
tags = ["scraping", "osint", "python"]
+++

Some internet research activities are based on not only present data, but also
on accessing historical data that was posted online. We will go through a simple 
example of how scraping pre-crawled pages from Internet Archive Wayback
Machine can be used to gather historical data for data science purposes. 
To look into Iowa inmate population trends, we will be scraping historical 
snapshots of Iowa Department of Corrections [inmate statistics page](https://doc-search.iowa.gov/dailystatistics). 
Data of interest is in "Current Count" and "Institution" columns of the table. 
For scraping we will use Python with requests and lxml modules. For dataviz we 
will use Jupyter, Pandas and Matplotlib.

WRITEME

Some open source projects relying on Internet Archive API:

* [gau](https://github.com/lc/gau) - a recon tool to fetch known URLs from several
sources, including Internet Archive.
* Bellingcat's [wayback-google-analytics](https://github.com/bellingcat/wayback-google-analytics)
is OSINT tool to dig up Google Analytics identifiers for finding associations
between websites.

