+++
author = "rl1987"
title = "Scraping Clutch for B2B company data"
date = "2024-04-12"
draft = true
tags = ["python", "web-scraping", "b2b"]
+++

[Clutch.co](https://clutch.co/) is a web portal serving as B2B service company
directory. One may want to scrape it to make a list of companies within a
service niche to target them with some form of outreach. Company name, website 
URL, phone number and maybe coordinates from the embedded map widget could
be fields of the dataset we would create by scraping this site. But the thing is, 
Clutch is fighting scraping attempts by using Cloudflare antibot service - 
naively fetching a page from this site gives us a 403 response with JS challenge.
So what do we do?

Some would suggest using anti-detect browser as foundation for the scraper, but 
let us not rush to that. Instead, let's work out what makes or breaks a request 
here. Open the site in Chrome, accept the cookies and let it pass the JS challenge. 
Now, by using "Copy as cURL" feature in Chrome DevTools we can get something like 
the following curl(1) command:

```bash
curl 'https://clutch.co/profile/testmatick' \
  -H 'authority: clutch.co' \
  -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \
  -H 'accept-language: en-GB,en-US;q=0.9,en;q=0.8' \
  -H 'cache-control: no-cache' \
  -H 'cookie: CookieConsent={stamp:%27gy8cYhc5rqyD+4wboFTjYwRZ3kmocvJU5dWpISe25EAYM1scKDNvWg==%27%2Cnecessary:true%2Cpreferences:false%2Cstatistics:false%2Cmarketing:false%2Cmethod:%27explicit%27%2Cver:1%2Cutc:1695021963851%2Cregion:%27lt%27}; exp_new-ab-test_attribute=1; exp_primary-cta-ab-test_attribute=old-main-CTA; __cf_bm=1Fxjs7RHjDX7mJRgzYLLodoV34MLcm0wFywRiYuqI0A-1708179657-1.0-ARy825yNViMh5Y/1qk+ul7/3KcNwb3kyyLNo+euY/dSC3f0123QWFZicuEcWZHDvEI0PFFzGb2A3IH++XuIto7c=; cf_clearance=2vwV27CEWNrT84e_nLo96kgOoihjSA2iBGBHBJvehAs-1708179658-1.0-AUS2KK3KRx6wX63hAVmC5YVDwczAz6d90pitbdBM6BIixlgYM/x1QaBMkzbT34dS2Trav72zccQ/zlvmoyicerE=' \
  -H 'pragma: no-cache' \
  -H 'sec-ch-ua: "Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-fetch-dest: document' \
  -H 'sec-fetch-mode: navigate' \
  -H 'sec-fetch-site: none' \
  -H 'sec-fetch-user: ?1' \
  -H 'upgrade-insecure-requests: 1' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36' \
  --compressed
```

Running this command in the shell does indeed give us a proper page, so it
seems neither TLS nor HTTP/2 fingerprinting is used. We see some browser-specific
headers here and we see some cookies being used. To narrow down what exactly is 
needed, we can remove some headers and relaunch the request - we discover that
only cookies and `user-agent` header is necessary. Now we can remove cookies one
by one and repeat the same kind of experiment. We find that both of `exp_` 
cookies can be removed without triggering the antibot.

So the cookies that are necessary seem to be:

1. `CookieConsent`
2. `__cf_bm`
3. `cf_clearance`

The latter two are directly related to Cloudflare's antibot products and are 
of prime importance to our objective.

We need to get these cookies somehow. Let us try using Bright Data's
[Scraping Browser](https://help.brightdata.com/hc/en-us/sections/13350440041873-Scraping-Browser) - 
a programmatically controllable web browser hosted for us in blocking-resistant
setup. Despite being hosted in the cloud it can be integrated with the usual
suspects of browser automation - Selenium, Playwright, Puppeteer. But we don't
need to implement the entire scraping flow with browser automation - we merely
have to use it just enough to get the CF cookies.

Let us rework the sample code from [documentation page](https://docs.brightdata.com/scraping-automation/scraping-browser/configuration)
to suit our objective:

```python
#!/usr/bin/python3

import asyncio
from playwright.async_api import async_playwright

# $ pip3 install playwright

from pprint import pprint

USERNAME = "[REDACTED]"
PASSWORD = "[REDACTED]"

AUTH = USERNAME + ":" + PASSWORD
SBR_WS_CDP = f"wss://{AUTH}@brd.superproxy.io:9222"


async def run(pw):
    print("Connecting to Scraping Browser...")
    browser = await pw.chromium.connect_over_cdp(SBR_WS_CDP)
    try:
        print("Connected! Navigating...")
        page = await browser.new_page()
        await page.goto("https://clutch.co/profile/devfortress", timeout=2 * 60 * 1000)
        cookies = await page.context.cookies()
        pprint(cookies)
    except Exception as e:
        print(e)
    finally:
        await browser.close()


async def main():
    async with async_playwright() as playwright:
        await run(playwright)


if __name__ == "__main__":
    asyncio.run(main())

```

We can easily convert this snippet to use synchronous Playwright API:

```python3
#!/usr/bin/python3

from playwright.sync_api import sync_playwright, Playwright

from pprint import pprint

USERNAME = "[REDACTED]"
PASSWORD = "[REDACTED]"

AUTH = USERNAME + ":" + PASSWORD
SBR_WS_CDP = f"wss://{AUTH}@brd.superproxy.io:9222"

def run(pw: Playwright):
    browser = pw.chromium.connect_over_cdp(SBR_WS_CDP)
    try:
        page = browser.new_page()
        page.goto("https://clutch.co", timeout=1 * 60 * 1000)
        cookies = page.context.cookies()
        pprint(cookies)
    except Exception as e:
        print(e)
    finally:
        browser.close()

def main():
    with sync_playwright() as playwright:
        run(playwright)

if __name__ == "__main__":
    main()


```

Once we got the cookies, we can proceed with scraping the data. There are three
levels to the scraping process we are going to implement:

1. Grabbing a list of business categories.
2. Traversing this list will give us bunch of links for company pages (each 
category URL points to a paged list of companies within a category - we have
to account for some overlap between categories).
3. Scraping each company page will gives us an item - a unit of data that is
to be saved into CSV file.

Since this involves cookies that we have to reuse between requests we want to
set up a requests session to use for scraping and recreate it when needed.
However there is a little complication - in this case TLS fingerprint is
also being checked, thus we need to use TLS client library to reproduce a 
fingerprint that looks realistic - like the one coming from real browser. We thus
use Playwright together with open source TLS client (`tls-client` from PIP) to 
prepare an equivalent of `requests.Session` object:

```python
import tls_client
from playwright.sync_api import sync_playwright, Playwright

USERNAME = "[REDACTED]"
PASSWORD = "[REDACTED]"
PROXY_URL = "[REDACTED]"

AUTH = USERNAME + ":" + PASSWORD
SBR_WS_CDP = f"wss://{AUTH}@brd.superproxy.io:9222"


def get_cookies(page_url):
    cookies = None

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(SBR_WS_CDP)
        try:
            page = browser.new_page()
            page.goto(page_url, timeout=1 * 60 * 1000)
            cookies = page.context.cookies()
            print("Got cookies:", cookies)
        except Exception as e:
            print(e)
        finally:
            browser.close()

    return cookies


def create_session(page_url):
    session = tls_client.Session(
        client_identifier="chrome120", random_tls_extension_order=True
    )

    session.headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "sec-ch-ua": '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.234 Safari/537.36",
    }

    cookies = get_cookies(page_url)

    for cookie in cookies:
        session.cookies.set(
            cookie.get("name"), cookie.get("value"), domain=cookie.get("domain")
        )

    session.proxies = {"http": PROXY_URL, "https": PROXY_URL}

    return session
```

When creating session we also set browser-like HTTP headers and integrate a proxy
service - in this case DC proxies are sufficient as long as we have the proper
cookies. Nobody seems to care that CF challenge was solved from different IP than
the requests we generate later (up to a point - sometimes we need to redo the
session creation step to proceed with scraping).

I elected to break down the scraping process into two scripts. The first one
sources list of companies by first scraping [Sitemap page](https://clutch.co/sitemap), 
then traversing the company lists to make a deduplicated list of profile URLs.
Not much to see there if you have read more of the posts on this blog. The second
script goes through profile URLs and scrapes some information from profile pages:

```python
#!/usr/bin/python3

import csv
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pprint import pprint
from urllib.parse import unquote
import time
import threading

from lxml import html

from tls_session import create_session, safe_get

sessions = dict()

def prepare_thread_session():
    sessions[threading.current_thread()] = create_session("https://clutch.co")

def scrape_company_page(company_url):
    session = sessions[threading.current_thread()]
    resp = safe_get(session, company_url)
    if resp is None or resp.status_code == 403:
        print("Retrying: {}".format(company_url))
        prepare_thread_session()
        session = sessions[threading.current_thread()]
        resp = safe_get(session, company_url)

    if resp is None:
        return None

    print(resp.url, resp.status_code)

    if resp.status_code != 200:
        return None

    tree = html.fromstring(resp.text)

    company_name = tree.xpath("//h1/a/text()")
    if len(company_name) == 1:
        company_name = company_name[0].strip()
    else:
        company_name = None

    # ...

    row = {
        "company_name": company_name,
        # ...
    }

    return row

FIELDNAMES = [
    "company_name",
    # ...
]


def main():
    company_urls = []

    in_f = open("lists.csv", "r")
    
    csv_reader = csv.DictReader(in_f)

    for row in csv_reader:
        company_urls.append(row['company_url'])

    in_f.close()
    
    out_f = open("pages.csv", "w+", encoding="utf-8")
    
    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator='\n')
    csv_writer.writeheader()

    with ThreadPoolExecutor(16, initializer=prepare_thread_session) as executor:
        for row in executor.map(scrape_company_page, company_urls):
            if row is None:
                continue
            pprint(row)
            csv_writer.writerow(row)

    out_f.close()

if __name__ == "__main__":
    main()

```

Some things to note here:

* `ThreadPoolExecutor` object from `concurrent.futures` was used to create and 
run a thread pool to make the scraping concurrent.
* For each thread we need a session that we initially create in thread initializer
function and also recreate on as-needed basis. The `sessions` dictionary is keyed
by the thread which allows each thread to unambiguously access the session it
created.
* Sometimes HTTPS requests fail with some exception (e.g. connection times out).
To prevent this from crashing the entire script we use `safe_get()` helper 
function. 

By using rather simple code I was able to scrape over 307 000 rows of company 
data with pretty trivial opex and not much development effort. The scraping
can be done overnight in a small VPS despite the first script being 
single-threaded and the second one using only 16 threads.

