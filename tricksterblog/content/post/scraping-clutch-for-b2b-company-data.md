+++
author = "rl1987"
title = "Scraping Clutch for B2B company data"
date = "2024-02-29"
draft = true
tags = ["python", "web-scraping"]
+++

[Clutch.co](https://clutch.co/) is a web portal serving as B2B service company
directory. One may want to scrape it to make a list of companies within a
service niche to target them with some form of outreach. But the thing is, 
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
need to use Playwright/Selenium/Puppeteer just enough to get the CF cookies.


