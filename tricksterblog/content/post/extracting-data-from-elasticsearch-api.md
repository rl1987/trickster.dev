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

If we go to [collection.carnegieart.org](https://collection.carnegieart.org/) 
with web browser we see a list of of various objects being presented with search
icon on the upper right corner of the page. Loading this page relies on 
elasticsearch API, as can be seen in Network tab of Chrome DevTools.

[TODO: screenshots]

For instance, the following request (represented by curl snippet) fetches
the first page worth of data:

```bash
curl 'https://collection.carnegieart.org/api/cmoa_objects/_msearch?' \
  -H 'authority: collection.carnegieart.org' \
  -H 'accept: application/json' \
  -H 'accept-language: en-GB,en-US;q=0.9,en;q=0.8' \
  -H 'authorization: Basic Y29sbGVjdGlvbnM6bzQxS0chTW1KUSRBNjY=' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/x-ndjson' \
  -H 'origin: https://collection.carnegieart.org' \
  -H 'pragma: no-cache' \
  -H 'referer: https://collection.carnegieart.org/' \
  -H 'sec-ch-ua: "Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36' \
  --data-raw $'{"preference":"results"}\n{"query":{"bool":{"must":[{"bool":{"must":[{"bool":{"must":[{"term":{"images.permitted":true}},{"exists":{"field":"images.filename"}}]}}]}}]}},"size":24,"sort":[{"acquisition_date":{"order":"desc"}}]}\n' \
  --compressed
```
