+++
author = "rl1987"
title = "Extracting data from elasticsearch API"
date = "2023-09-26"
draft = true
tags = ["scraping", "python"]
+++

Elasticsearch is open source server software that acts both as database and
search engine, based on Apache Lucene library. It can be used to build 
distributed clusters for indexing and searching Enterprise-level amounts of
data. Some sites that present large, searchable, mostly-textual datasets to
the end user are based on elasticsearch as their backend data store and have
frontend code talking directly to the API of elasticsearch. If the frontend
can talk directly to elasticsearch, so can we as web scraper developers with all
the benefits the flexible data search engine can bring. A specific example is 
the website of Carnegie Museum of Art. To see how the trick works, we will be 
scraping this site today.


