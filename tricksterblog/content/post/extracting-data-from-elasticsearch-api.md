+++
author = "rl1987"
title = "Extracting data from elasticsearch API"
date = "2023-10-15"
draft = true
tags = ["scraping", "python"]
+++

[Elasticsearch](https://github.com/elastic/elasticsearch) is open 
source server software that acts both as database and search engine, based on 
Apache Lucene library. It can be used to build distributed clusters for 
indexing and searching Enterprise-level amounts of data. 
Some sites that present large, searchable, mostly-textual datasets to
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

[Screenshot 1](/2023-10-04_18.16.04.png)
[Screenshot 2](/2023-10-04_18.16.15.png)

Some things are notable here. A `content-type` header is `application/x-ndjson` 
which means Newline-Delimited JSON is provided in the POST request payload. 
That entails not a single JSON array or object, but a sequence of JSON objects -
one per line. The second line provides a configuration for search query 
(pretty-printed for readability):

```json
{
  "query": {
    "bool": {
      "must": [
        {
          "bool": {
            "must": [
              {
                "bool": {
                  "must": [
                    {
                      "term": {
                        "images.permitted": true
                      }
                    },
                    {
                      "exists": {
                        "field": "images.filename"
                      }
                    }
                  ]
                }
              }
            ]
          }
        }
      ]
    }
  },
  "size": 24,
  "sort": [
    {
      "acquisition_date": {
        "order": "desc"
      }
    }
  ]
}
```

At `query` key we have some nested predicate that basically requires object 
images to be available ("Has Images" checkbox is on by default). At `size`
we have a page size and at `sort` key we have sorting configuration.

If we go to next page we start having another key here - `from` that enables
pagination by search result offset.

A regular JSON payload is available in the payload of response and has a great
deal of information on the museum objects. So the good news is that we don't
need to parse any kind of HTML here and can fully rely on pre-structured
data that we can access through elasticsearch API. The entire dataset of
Carnegie Museum of Art object catalog can be gathered solely by doing API 
scraping.

[Screenshot 3](/2023-10-04_18.16.34.png)

There is also the `authorization` header here with Base64-encoded API 
credentials. This does not add any security as we can simply decode the 
encoded part of the header and recover username/password that frontend code uses:

```
$ echo "Y29sbGVjdGlvbnM6bzQxS0chTW1KUSRBNjY=" | base64 -d
collections:o41KG!MmJQ$A66
```

Now, if we uncheck the "Has Image" checkbox the second line in the request
payload becomes even simpler:

```json
{
  "query": {
    "match_all": {}
  },
  "size": 24,
  "sort": [
    {
      "acquisition_date": {
        "order": "desc"
      }
    }
  ]
}
```

[Screenshot 4](/2023-10-04_18.47.47.png)

Now the query covers all the data (91668 results). But there's a little problem -
the elasticsearch Search API that is used here is not meant to provide all the
search results. For that purpose we should be using the 
[Scroll API](https://www.elastic.co/guide/en/elasticsearch/reference/current/scroll-api.html)
that is designed to provide a paginated access to search results after the 
first Search API request is performed.

WRITEME

Since we have access to the API of elasticsearch database, we can use it to 
develop unofficial/adversarial integrations by either doing the API calls
directly as in above example of by using one of the elasticsearch client 
libraries. There are two official options for Python:

* [elasticsearch-py](https://github.com/elastic/elasticsearch-py) for bridging
the gap between ES API construct and Python modules.
* [elasticsearch-dsl-py](https://github.com/elastic/elasticsearch-dsl-py) for a
higher order API that provides a more convenient way to work with database while
not straying too far from the JSON-based API.

