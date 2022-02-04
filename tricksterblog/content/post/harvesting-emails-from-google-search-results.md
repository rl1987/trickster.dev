+++
author = "rl1987"
title = "Harvesting emails from Google search results"
date = "2022-02-07"
draft = true
tags = ["web-scraping", "python", "growth-hacking"]
+++

Automated gathering of email addresses is known as email harvesting. Suppose we want to gather the
email addresses of certain kinds of individuals, such as influencers or content creators. This
can be accomplished through certain less-known features of Google. For example, `site:` operator
limits search results to a given domain. Double-quoting something forces Google to provide 
exact matches on the quoted text. Boolean operators (`AND`, `OR`) are also supported.

Google caps the number of results to about 300 per query, but we can mitigate this limitation
by breaking down search space into smaller segments across multiple search queries. In this 
example, we are going to search for people not only by keyword but also by location - for
each search, we will be using a combination of keywords with a Boolean operator to tell the search
engine to match on a combination of strings.

We will be implementing email harvesting from social media profiles that can be found via Google.

One more thing to address is Google's rate-limiting on excessive searching. If we launch too many
search engines in a short timeframe Google will start asking for captcha solutions, which we want
to avoid. For this purpose, we will be sending the requests through a proxy pool.

Let us prepare the search query components first. In sites.txt, we put the list of domain names
we want to find the results in:

```
instagram.com
tiktok.com
```

In q1.txt we put list of domain names we want to find emails in, prefix by `@` character:

```
@gmail.com
@yahoo.com
```

In q2.txt we put a list of locations we want to find people in:

```
San Francisco
New York
```

In q3.txt we put a list of occupational keywords:

```
influencer
model
content creator
```

Our code will be doing nested loops across all permutations of the above things, scraping Google
search result pages, and applying regular expressions to extract email addresses.

Depending on your exact needs, you may want to use simpler or more complex regular expression
to match email addresses in the result snippet text. For some, examples see the following
Stack Overflow pages:

* [How can I validate an email address using a regular expression?](https://stackoverflow.com/questions/201323/how-can-i-validate-an-email-address-using-a-regular-expression)
* [regex extract email from strings](https://stackoverflow.com/questions/42407785/regex-extract-email-from-strings)

To get HTML page with search results, we are going to send HTTP GET requests to `https://www.google.com/search` with
the following parameters:

* `q` - search query.
* `start` - initial index of start results.
* `num` - number of search results per page (we will be using max value: 100).

We also set the `User-Agent` header to match that of a regular browser, as Google would block
our requests otherwise.

The complete script for harvesting email is as follows:

```python
#!/usr/bin/python3

import csv
from pprint import pprint
import re
import time
import os

import requests
from lxml import html

FIELDNAMES = ["result_url", "title", "text", "email"]

def scrape_result_page(query, start, num):
    url = "https://www.google.com/search"

    params = {
        "q": query,
        "start": start,
        "num": num,
    }

    while True:
        resp = requests.get(url, params=params, verify=False)
        print(resp.url)

        if resp.status_code == 200:
            break

        time.sleep(1)
        continue

    tree = html.fromstring(resp.text)

    rows = []

    result_divs = tree.xpath('//div[@class="jtfYYd"]')

    for result_div in result_divs:
        result_url = result_div.xpath(".//a/@href")
        if len(result_url) >= 1:
            result_url = result_url[0]
        else:
            result_url = ""

        title = result_div.xpath(".//h3/text()")
        if len(title) == 1:
            title = title[0]
        else:
            title = ""

        snippet_div = result_div.xpath('.//div[@style="-webkit-line-clamp:2"]')
        if len(snippet_div) == 1:
            snippet = snippet_div[0].text_content()
        else:
            snippet = ""

        row = {
            "result_url": result_url,
            "title": title,
            "text": snippet,
        }

        # https://stackoverflow.com/questions/17681670/extract-email-sub-strings-from-large-document
        m = re.search(
            r"(?:\.?)([\w\-_+#~!$&\'\.]+(?<!\.)(@|[ ]?\(?[ ]?(at|AT)[ ]?\)?[ ]?)(?<!\.)[\w]+[\w\-\.]*\.[a-zA-Z-]{2,3})(?:[^\w])",
            snippet + " " + title,
        )

        if m is not None:
            row["email"] = m.groups()[0]
        else:
            continue

        rows.append(row)

    return rows, len(result_divs) < num


def scrape_results(query):
    start = 0
    num = 100

    while True:
        rows, done = scrape_result_page(query, start, num)

        for row in rows:
            yield row

        if done:
            break

        start += num


def main():
    in_f = open("sites.txt", "r")
    sites = in_f.read().strip().split("\n")
    in_f.close()

    in_f = open("q1.txt", "r")
    queries1 = in_f.read().strip().split("\n")
    in_f.close()

    in_f = open("q2.txt", "r")
    queries2 = in_f.read().strip().split("\n")
    in_f.close()

    in_f = open("q3.txt", "r")
    queries3 = in_f.read().strip().split("\n")
    in_f.close()

    out_f = open("emails.csv", "w", encoding="utf-8")

    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()

    for site in sites:
        for q1 in queries1:
            for q2 in queries2:
                for q3 in queries3:
                    query = 'site:{} "{}" AND "{}" AND "{}"'.format(site, q1, q2, q3)

                    for row in scrape_results(query):
                        pprint(row)
                        csv_writer.writerow(row)

    out_f.close()


if __name__ == "__main__":
    main()

```

This code expects `HTTPS_PROXY` environment variable with proxy URL. For this purpose, we can
create a SERP proxy zone on BrightData.

Note that Google is constantly updating it's frontend, which may cause the code to break.
For example, you may need to update XPath queries for parts of page being extracted.
To sidestep this issue, you may want to check out some SaaS tools that provide an API for Google
result scraping:

* [Bright Data Search Engine Crawler](https://brightdata.com/products/search-engine-crawler)
* [SerpAPI](https://serpapi.com/)
* [ZenSERP](https://zenserp.com/)
* [SERPStack](https://serpstack.com/)

