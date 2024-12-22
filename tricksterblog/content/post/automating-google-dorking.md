+++
author = "rl1987"
title = "Automating Google Dorking"
date = "2021-12-19"
tags = ["python", "osint", "security"]
+++

There is more to using Google than searching by keywords, phrases and natural language questions. Google
also has advanced features that can empower users to be extra specific with their searches.

To search for an exact phrase, wrap it in double quotes, for example:

```
"top secret"
```

To search for documents with a specific file extension, use `filetype:` operator:

```
filetype:pdf "top secret'
```

To search for results in a specific domain, use `site:` operator. This can also be used with top-level
domain, for example: 

```
site:gov filetype:pdf "top secret"
```

You may also watch to narrow down results based on part of URL that is not a domain name. This
can be achieved with `inurl:` operator:

```
site:gov inurl:declassified filetype:pdf "top secret"
```

Google also supports the usage of Boolean operators in search queries, for example:

```
ethics AND (OSINT OR cybersecurity)
```

Google dorking is using advanced search queries to find things that are not necessarily meant to be exposed
to the public internet. For example, to find some webcams, one might search:

```
intitle:"Live View/ — AXIS"
```

[Google Hacking Database](https://www.exploit-db.com/google-hacking-database) is a section of ExploitDB portal
that provides pre-written search queries that are meant to find things relevant for security. OSINT investigators
can use them to discover various pieces of information. Bounty hunters and penetration testers can use these 
queries as part of the target recon phase. Likewise, security professionals working on defensive side can also benefit
when evaluating the security of systems they are protecting. Some of these queries reveal plaintext passwords or
private keys.  I don't recommend using these for any malicious or questionable purposes, but if a site has a 
bug bounty program it might be worthwhile to report it.

How can one automate Google dorking? One way is to simply scrape Google search engine results pages. Google
does not exactly like that and will throw a captcha at you if they detect too many requests too quickly from a
single IP address. However, as long as one is using a proper proxy pool Google SERP scraping is not difficult
and can be done with not too much effort by knowing a little XPath/CSS and using something like Python with 
[lxml](https://lxml.de/) module.

Another way is to use one of the many SERP scraping SaaS solutions, like:

* [ZenSerp](https://zenserp.com/)
* [SerpAPI](https://serpapi.com/)
* [DataForSEO](https://dataforseo.com/)
* [Bright Data Search Engine Crawler](https://brightdata.com/products/search-engine-crawler)

These options are fairly obvious to developers working with scraping and automation projects. However, there is
a third, relatively obscure option. The little known fact is that Google search has an API, kind of. They call this
[Programmable Search](https://developers.google.com/custom-search). It's meant as a way to let people integrate
the Google search engine into their own sites. If you have seen sites having a widget to search content with Google
then this is how these sites are integrating with Google. Note that only the first 100 search requests per day are free,
but after that Google will bill you $5 per 1000 queries.

To set up your access to this API you need to follow the following steps. 

First, you need to set up a Custom Search Engine at 
[Programmable Search control panel](https://programmablesearchengine.google.com/create/new).
Don't worry too much about what to put into "Sites to search" textfield, as you will be able to edit them later.
If you have a particular domain for a site you want to search (e.g. from a bug bounty platform) it would be useful
to limit results to that. Alternatively, you can put in bunch of wildcard entries for multiple popular TLDs:

```
*.gov
*.edu
*.com
*.net
*.org
```

Type in some name into "Name of the search engine" text field. Solve the captcha and press CREATE button. 
Now choose the search engine you just created under "Edit search engine" text on the left hand side of 
the page.  If needed, flip a "Search the entire web" switch in the settings. Note the search engine 
ID as we will need it for API requests.

Press "Get Started" button on "Custom Search JSON API" row. This will take you to page called
[Custom Search JSON API: Introduction](https://developers.google.com/custom-search/v1/introduction).
Press "Get a key" button that will let you choose a Google Cloud project. Create a new one if needed.
Once the project is selected, you will be given the API key.

Google provides an [API reference](https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list)
with all the parameters, but for the simplest API call we only need the following:

* `cx` - search engine ID.
* `key` - API key.
* `q` - search query.

The following curl snippet exemplifies API call that we are interested in:

```
$ curl "https://www.googleapis.com/customsearch/v1?key=[REDACTED]&cx=[REDACTED]&q=secret"
```

The following simple Python script provides an example of using this API for traversing
across multiple search queries and saving the results into CSV file.

```python
#!/usr/bin/python3

import csv
from pprint import pprint

import requests

SEARCH_ENGINE_ID = "[REDACTED]"
API_KEY = "[REDACTED]"

FIELDNAMES = ["query", "result_url", "result_title", "result_snippet"]


def main():
    in_f = open("queries.txt", "r", encoding="utf-8")
    out_f = open("results.csv", "w", encoding="utf-8")

    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()

    for query in in_f:
        query = query.strip()
        print(query)

        params = {
            "cx": SEARCH_ENGINE_ID,
            "key": API_KEY,
            "q": query,
        }

        resp = requests.get("https://www.googleapis.com/customsearch/v1", params=params)
        print(resp.url)

        json_dict = resp.json()

        for item_dict in json_dict.get("items", []):
            row = {
                "query": query,
                "result_url": item_dict.get("link"),
                "result_title": item_dict.get("title"),
                "result_snippet": item_dict.get("snippet"),
            }

            pprint(row)

            csv_writer.writerow(row)

    out_f.close()
    in_f.close()


if __name__ == "__main__":
    main()
```

If needed, you can use `start` and `num` parameters to get more pages
from API. However, you are allowed to get only up to 100 results per query
even if there are more available. 

You may also want to check out Google's 
[Knowledge Graph Search API](https://developers.google.com/knowledge-graph)
that allows one to search for entities like people, companies, places, and so on.
