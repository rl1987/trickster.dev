+++
author = "rl1987"
title = "Abusing GOAT mobile API for scraping and automation"
date = "2023-08-14"
draft = true
tags = ["scraping", "automation"]
+++

GOAT is an online platform for retail sale and reselling of certain consumer
products - primarily sneakers, apparel and electronics. It is estimated to 
have about 50 million active users that include some one million sellers. When
there's a major userbase, there's a potential to extract monetary benefit by
scraping the data and/or running some automations. But 1661 Inc., a company that
is developing GOAT don't want us to do that. GOAT is one of the websites that 
proactively fight automated traffic. For example, merely trying load the front 
page in Scrapy shell gives us a Cloudflare error.

[TODO: screenshot]

So we have to proceed differently. One trick from grayhat automation arsenal is
to MITM mobile app traffic to work out the exact API calls being done against 
the backend system, then replay them programmatically. A first example will be
a simple API scraping to extract data. Another will be demonstrating how mobile
API can be abused to automate user actions.

We will be using [mitmproxy](https://mitmproxy.org/) to intercept GOAT API
traffic. The setup in question is described in 
[earlier post](/post/setting-up-mitmproxy-with-ios15/), except that a newer iOS
version is used on the iPhone. 

When we run the app and press "Start browsing" button we see quite a bit of
traffic in mitmproxy TUI. Some things to notice here:

* Early in the app lifecycle it sends a request to PerimeterX API. This means
that PerimeterX is also used to fight automation.
* Some requests have `x-px-authorization` and `x-px-original-token` headers
that are related to PerimeterX. Furthermore, `__cf_bm` cookie is present on
some requests.
* There's `authorization` header with empty value. We expect this value to
be set when app is being used after logging in.
* Some requests go to goat.cnstrc.com domain and are not covered by PX/CF.

Let us start with the simple stuff first. Product data scraping is a common
thing that web scraper developers do. So let's do that, but through the mobile
API. On the mobile GUI we access the Search tab, type in a search query, press
`z` to clean the flows captured by mitmproxy and then press the search button.

[TODO: screenshots]

We see one request to goat.cnstrc.com and some more requests to images.goat.com.

[TODO: screenshot]

The first one is of primary interest to us, as it seems to return some subset
of product data in the JSON payload. Last component of the URL path is the
search query that was typed into the app.

We want to export this request as curl command. We position the curson on it
in the flow list view, press `e` and choose `1) curl` from list of options in
the little dialog box. Then we type the file path (e.g. `search.curl`) into 
bottom part of user interface.

```bash
curl -H 'accept: */*' --compressed -H 'user-agent: GOAT/19 CFNetwork/1410.0.3 Darwin/22.6.0' -H 'accept-language: en-GB,en;q=0.9' -H 'x-emb-id: 7E2DEE62833C40A0B733085027D1A5BC' 'https://goat.cnstrc.com/search/gtx?key=key_XT7bjdbvjgECO5d8&page=1&fmt_options%5Bhidden_fields%5D=gp_lowest_price_cents_2&fmt_options%5Bhidden_facets%5D=gp_lowest_price_cents_2&fmt_options%5Bhidden_fields%5D=gp_instant_ship_lowest_price_cents_2&fmt_options%5Bhidden_facets%5D=gp_instant_ship_lowest_price_cents_2&features%5Bdisplay_variations%5D=true&feature_variants%5Bdisplay_variations%5D=matched&variations_map=%7B%22dtype%22:%22object%22,%22group_by%22:%5B%7B%22name%22:%22product_condition%22,%22field%22:%22data.product_condition%22%7D,%7B%22name%22:%22box_condition%22,%22field%22:%22data.box_condition%22%7D%5D,%22values%22:%7B%22min_regional_instant_ship_price%22:%7B%22field%22:%22data.gp_instant_ship_lowest_price_cents_2%22,%22aggregation%22:%22min%22%7D,%22min_regional_price%22:%7B%22field%22:%22data.gp_lowest_price_cents_2%22,%22aggregation%22:%22min%22%7D%7D%7D'
```

By putting this into [curlconverter](https://curlconverter.com/) we get the 
following Python snippet:

```python
import requests

headers = {
    'accept': '*/*',
    'user-agent': 'GOAT/19 CFNetwork/1410.0.3 Darwin/22.6.0',
    'accept-language': 'en-GB,en;q=0.9',
    'x-emb-id': '7E2DEE62833C40A0B733085027D1A5BC',
}

response = requests.get(
    'https://goat.cnstrc.com/search/gtx?key=key_XT7bjdbvjgECO5d8&page=1&fmt_options%5Bhidden_fields%5D=gp_lowest_price_cents_2&fmt_options%5Bhidden_facets%5D=gp_lowest_price_cents_2&fmt_options%5Bhidden_fields%5D=gp_instant_ship_lowest_price_cents_2&fmt_options%5Bhidden_facets%5D=gp_instant_ship_lowest_price_cents_2&features%5Bdisplay_variations%5D=true&feature_variants%5Bdisplay_variations%5D=matched&variations_map=%7B%22dtype%22:%22object%22,%22group_by%22:%5B%7B%22name%22:%22product_condition%22,%22field%22:%22data.product_condition%22%7D,%7B%22name%22:%22box_condition%22,%22field%22:%22data.box_condition%22%7D%5D,%22values%22:%7B%22min_regional_instant_ship_price%22:%7B%22field%22:%22data.gp_instant_ship_lowest_price_cents_2%22,%22aggregation%22:%22min%22%7D,%22min_regional_price%22:%7B%22field%22:%22data.gp_lowest_price_cents_2%22,%22aggregation%22:%22min%22%7D%7D%7D',
    headers=headers,
)
```

I don't exactly like that it didn't decode the URL parameters into Python `dict`,
but this is a starting point for the script to be written.

We see that there's a `page` parameter with values starting from one. This 
covers the API pagination aspect.

In case you are wondering about `x-emb-id` header it is related to 
[mobile analytics solution](https://embrace.io/docs/ios/faq/#can-trace-ids-for-network-requests-be-captured) 
provided by Embrace Mobile, Inc.

The next step is getting some product details via API. When we tap on one of the
search results we see a bunch of HTTPS requests, most of them being made to
subdomains of goat.com domain.

Let us explore what we have here. There's a request to product template
endpoint `/api/v1/product_templates/.../show_v2` that takes product URL slug
(e.g. `terrex-swift-r2-mid-gtx-triple-black-cm7500`) as part of URL path
and gives the app a numeric product template ID to be used in some of the 
further API calls. It also provides some data is common across all product 
variants.  Our code will reproduce this API call with slug value that it got 
from search API to find out the `productTemplateID` value. Like we did with 
search API request, we export this one to curl snippet:

```bash
curl -H 'x-px-authorization: 3' -H 'accept: application/json' -H 'authorization: Token token=""' --compressed -H 'accept-language: en-GB,en;q=0.9' -H 'x-emb-st: 1691934124434' -H 'user-agent: GOAT/2.62.0 (iPhone; iOS 16.6; Scale/2.00) Locale/en' -H 'x-emb-id: A131256965044D838D97E9AEC3CC32DE' -H 'x-px-original-token: 3:7b9f8feffc454bb265869bb69319201a10c0733ded5f64415904867ca6015448:V3kOFKugd0IYEzhYfgTK4QOh8dWCzZH04C4uoGYEfOekVmjMvCYLle7yVImUv8bSOoVChlY3FPELVmFZLboPxA==:1000:V6naWWAGfhIA54bPIFXyWPSpd7e9WmoWghqXoB1xwiAb0TVePEULt5nHoZFhWkpg1E4ZjMtwt1N9yfV2HCYOklHUqUy+oaAlYkACXQLwqsD21d70W55yb0UY9qHQHxY9zQcr6th//3ckUVLU/v1yWhZt/GV9jNyf6EesLG9fw+gqMWPhrpi8bDT1j5eeTR9BLmWMqrY3hmQSYRc9C7K5pQ==' -H 'cookie: __cf_bm=SHyG5WOKr777DofsXNbK3U29rw2zT0.FAfklx3N4xlA-1691934028-0-AUJcAbBlN7VoM9Sv8KU4ADRc7kRMROE5dN8u/rsVpl+cxdtwaLQTX/D/tIGlWKDEjaZfMbkE+PaMCzCrlGheIbI=' -H 'cookie: currency=EUR' https://www.goat.com/api/v1/product_templates/terrex-swift-r2-mid-gtx-triple-black-cm7500/show_v2
```

We also convert this snippet to Python:

```python
import requests

cookies = {
    '__cf_bm': 'SHyG5WOKr777DofsXNbK3U29rw2zT0.FAfklx3N4xlA-1691934028-0-AUJcAbBlN7VoM9Sv8KU4ADRc7kRMROE5dN8u/rsVpl+cxdtwaLQTX/D/tIGlWKDEjaZfMbkE+PaMCzCrlGheIbI=',
    'currency': 'EUR',
}

headers = {
    'x-px-authorization': '3',
    'accept': 'application/json',
    'authorization': 'Token token=""',
    'accept-language': 'en-GB,en;q=0.9',
    'x-emb-st': '1691934124434',
    'user-agent': 'GOAT/2.62.0 (iPhone; iOS 16.6; Scale/2.00) Locale/en',
    'x-emb-id': 'A131256965044D838D97E9AEC3CC32DE',
    'x-px-original-token': '3:7b9f8feffc454bb265869bb69319201a10c0733ded5f64415904867ca6015448:V3kOFKugd0IYEzhYfgTK4QOh8dWCzZH04C4uoGYEfOekVmjMvCYLle7yVImUv8bSOoVChlY3FPELVmFZLboPxA==:1000:V6naWWAGfhIA54bPIFXyWPSpd7e9WmoWghqXoB1xwiAb0TVePEULt5nHoZFhWkpg1E4ZjMtwt1N9yfV2HCYOklHUqUy+oaAlYkACXQLwqsD21d70W55yb0UY9qHQHxY9zQcr6th//3ckUVLU/v1yWhZt/GV9jNyf6EesLG9fw+gqMWPhrpi8bDT1j5eeTR9BLmWMqrY3hmQSYRc9C7K5pQ==',
    # 'cookie': '__cf_bm=SHyG5WOKr777DofsXNbK3U29rw2zT0.FAfklx3N4xlA-1691934028-0-AUJcAbBlN7VoM9Sv8KU4ADRc7kRMROE5dN8u/rsVpl+cxdtwaLQTX/D/tIGlWKDEjaZfMbkE+PaMCzCrlGheIbI=; currency=EUR',
}

response = requests.get(
    'https://www.goat.com/api/v1/product_templates/terrex-swift-r2-mid-gtx-triple-black-cm7500/show_v2',
    cookies=cookies,
    headers=headers,
)
```

For the sake of example, we will save product name, main image URL and SKU from
the API response here.

We also want to save some price data. The part of UI that shows prices and last
sale amounts is populated by the `/api/v2/product_variants/buy_bar_data`
endpoint. We extract the curl snippet from mitmproxy again:

```bash
curl -H 'x-px-authorization: 3' -H 'accept: application/json' -H 'authorization: Token token=""' --compressed -H 'accept-language: en-GB,en;q=0.9' -H 'x-emb-st: 1691934124855' -H 'user-agent: GOAT/2.62.0 (iPhone; iOS 16.6; Scale/2.00) Locale/en' -H 'x-emb-id: 9E8BF79CF66F4912A122C3C38F872E0E' -H 'x-px-original-token: 3:7b9f8feffc454bb265869bb69319201a10c0733ded5f64415904867ca6015448:V3kOFKugd0IYEzhYfgTK4QOh8dWCzZH04C4uoGYEfOekVmjMvCYLle7yVImUv8bSOoVChlY3FPELVmFZLboPxA==:1000:V6naWWAGfhIA54bPIFXyWPSpd7e9WmoWghqXoB1xwiAb0TVePEULt5nHoZFhWkpg1E4ZjMtwt1N9yfV2HCYOklHUqUy+oaAlYkACXQLwqsD21d70W55yb0UY9qHQHxY9zQcr6th//3ckUVLU/v1yWhZt/GV9jNyf6EesLG9fw+gqMWPhrpi8bDT1j5eeTR9BLmWMqrY3hmQSYRc9C7K5pQ==' -H 'cookie: __cf_bm=SHyG5WOKr777DofsXNbK3U29rw2zT0.FAfklx3N4xlA-1691934028-0-AUJcAbBlN7VoM9Sv8KU4ADRc7kRMROE5dN8u/rsVpl+cxdtwaLQTX/D/tIGlWKDEjaZfMbkE+PaMCzCrlGheIbI=' -H 'cookie: currency=EUR' 'https://www.goat.com/api/v1/product_variants/buy_bar_data?countryCode=LT&productTemplateId=terrex-swift-r2-mid-gtx-triple-black-cm7500'
```

The corresponding Python snippet is:

```python
import requests

cookies = {
    '__cf_bm': 'SHyG5WOKr777DofsXNbK3U29rw2zT0.FAfklx3N4xlA-1691934028-0-AUJcAbBlN7VoM9Sv8KU4ADRc7kRMROE5dN8u/rsVpl+cxdtwaLQTX/D/tIGlWKDEjaZfMbkE+PaMCzCrlGheIbI=',
    'currency': 'EUR',
}

headers = {
    'x-px-authorization': '3',
    'accept': 'application/json',
    'authorization': 'Token token=""',
    'accept-language': 'en-GB,en;q=0.9',
    'x-emb-st': '1691934124855',
    'user-agent': 'GOAT/2.62.0 (iPhone; iOS 16.6; Scale/2.00) Locale/en',
    'x-emb-id': '9E8BF79CF66F4912A122C3C38F872E0E',
    'x-px-original-token': '3:7b9f8feffc454bb265869bb69319201a10c0733ded5f64415904867ca6015448:V3kOFKugd0IYEzhYfgTK4QOh8dWCzZH04C4uoGYEfOekVmjMvCYLle7yVImUv8bSOoVChlY3FPELVmFZLboPxA==:1000:V6naWWAGfhIA54bPIFXyWPSpd7e9WmoWghqXoB1xwiAb0TVePEULt5nHoZFhWkpg1E4ZjMtwt1N9yfV2HCYOklHUqUy+oaAlYkACXQLwqsD21d70W55yb0UY9qHQHxY9zQcr6th//3ckUVLU/v1yWhZt/GV9jNyf6EesLG9fw+gqMWPhrpi8bDT1j5eeTR9BLmWMqrY3hmQSYRc9C7K5pQ==',
    # 'cookie': '__cf_bm=SHyG5WOKr777DofsXNbK3U29rw2zT0.FAfklx3N4xlA-1691934028-0-AUJcAbBlN7VoM9Sv8KU4ADRc7kRMROE5dN8u/rsVpl+cxdtwaLQTX/D/tIGlWKDEjaZfMbkE+PaMCzCrlGheIbI=; currency=EUR',
}

params = {
    'countryCode': 'LT',
    'productTemplateId': 'terrex-swift-r2-mid-gtx-triple-black-cm7500',
}

response = requests.get(
    'https://www.goat.com/api/v1/product_variants/buy_bar_data',
    params=params,
    cookies=cookies,
    headers=headers,
)
```

One last thing to note is that some APIs are meant to be used after login 
and thus don't provide any data at this point.




