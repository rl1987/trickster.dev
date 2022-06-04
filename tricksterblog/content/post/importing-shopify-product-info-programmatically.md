+++
author = "rl1987"
title = "Importing Shopify product info programmatically"
date = "2022-06-04"
tags = ["python", "automation"]
+++

Sometimes one would scrape eCommerce product data for the purpose of reselling these
products. For example, a retail ecommerce company might be sourcing their products
from a distributor that does not provide an easy way to integrate into Shopify
store. This problem can be solved through web scraping. Once data is scraped,
it can be imported into Shopify store. 

One way to do that is to wrangle the product dataset into file(s) that heed
the [Shopify product CSV schema](https://help.shopify.com/en/manual/products/import-export/using-csv)
and import it via Shopify store admin dashboard. However this entails
human intervention and may be considered to be an inferior solution when
compared to something fully automatic.

Good news is that Shopify does provide a public API for store administration
tasks, including product importing and updating. We can integrate this API with
our web scraping solution.

We will be showing how the REST version of [Shopify Admin API](https://shopify.dev/api/admin-rest)
can be used to upload pre-scraped product dataset. But first, we need to get
some API credentials that we can use. The following assumes you having a
development store that you can play with.

We need to create something called Custom App. In your Shopify admin dashboard, go to Apps tab
and press "Develop apps" button on the top. In the next page, press "Create an app" button on the top.
The modal view will ask for app name. Once app is created, we need to configure API scopes.
Press "Configure Admin API scopes" button in the new page. Bunch of checkboxes will be presented to you.
For the purpose of this task, we need to choose `read_products` and `write_products`. Now press the
"Save" button on the bottom of the page. Now press the "Install app" button on the top of the page.
You will be given a chance to see and copy the Admin API access token. Make sure you save it somewhere
else before clicking away from the page. Don't worry about API key and secret - we won't be needing
them here.

Let us get familiar with the Shopify product data model. There are three entities of interest to us:
product, product variant and product image. Product is the parent object that may have one or more
variant associated to it and some images as well. Furthemore, product variants are allowed to make
secondary association to product images (e.g. product variant of specific color will point to 
corresponding image). For the exact details, see the following pages on Shopify developer portal:

* Product - https://shopify.dev/api/admin-rest/2022-04/resources/product#top
* ProductVariant - https://shopify.dev/api/admin-rest/2022-04/resources/product-variant#top
* ProductImage - https://shopify.dev/api/admin-rest/2022-04/resources/product-image#top

We will be importing product CSV file that has the following columns:

* `title` - product title.
* `asin` - Amazon product ID.
* `price` - price in GBP, with pound character included. Sometimes range of prices.
* `brand` - name of brand that sometimes need a little cleanup.
* `product_details` - product description.
* `breadcrumbs` - slash-separated list of breadcrumb strings.
* `images_list` - JSON array containing URLs to product images

Let us discuss the following code that implements the importing.

```python
#!/usr/bin/python3

import csv
import json
import time
from pprint import pprint

import requests

API_TOKEN = None


def check_if_present(store_name, title, asin):
    headers = {"Content-Type": "application/json", "X-Shopify-Access-Token": API_TOKEN}

    api_url = "https://{}.myshopify.com/admin/api/2022-04/products.json".format(
        store_name
    )

    params = {"title": title}

    resp = requests.get(api_url, headers=headers, params=params, timeout=10)

    json_dict = resp.json()

    if json_dict.get("products") is None or len(json_dict.get("products")) == 0:
        return False

    for prod_dict in json_dict.get("products"):
        variant = prod_dict.get("variants")[0]
        if variant.get("sku") == asin:
            return True

    return False


def import_product(store_name, product):
    headers = {"Content-Type": "application/json", "X-Shopify-Access-Token": API_TOKEN}

    api_url = "https://{}.myshopify.com/admin/api/2022-04/products.json".format(
        store_name
    )

    payload = {
        "product": {
            "title": product.get("title"),
            "body_html": product.get("product_details"),
            "vendor": product.get("brand", "")
            .replace("Visit the ", "")
            .replace(" Store", ""),
            "tags": product.get("breadcrumbs", "").split("/"),
            "published": True,
            "options": [
                {"name": "Size"},
            ],
            "product_type": "Shoes",
            "images": [],
            "variants": [
                {
                    "sku": product.get("asin"),
                    "price": product.get("price").split(" - ")[-1].replace("£", ""),
                    "requires_shipping": True,
                }
            ],
        }
    }

    i = 1

    for img_url in json.loads(product.get("images_list")):
        payload["product"]["images"].append(
            {
                "src": img_url,
                "position": i,
            }
        )

        i += 1

    pprint(payload)

    resp = requests.post(api_url, headers=headers, json=payload, timeout=10)

    if resp.status_code != 201:
        print("Error: Import to shopify failed!")
        print(resp.text)


def main():
    global API_TOKEN

    store_name = input("Enter store name (part of subdomain before .myshopify.com): ")

    t_f = open("api_token.txt", "r")
    API_TOKEN = t_f.read()
    t_f.close()

    in_f = open("amazon_uk_shoes_dataset.csv", "r")

    csv_reader = csv.DictReader(in_f)

    for row in csv_reader:
        if row.get("price") == "":
            continue

        if not check_if_present(store_name, row.get("title"), row.get("asin")):
            import_product(store_name, row)
        else:
            print(
                "{} ({}) already present - skipping...".format(
                    row.get("title"), row.get("asin")
                )
            )

        time.sleep(0.5)

    in_f.close()


if __name__ == "__main__":
    main()
```

In the `main()` function we read CSV file line by line. We skips rows that do not have 
price defined. 

Next, we call `check_if_present()` function that will check if product matching title from
CSV with variant SKU matching `asin` field is already present on the store. This is necessary
to prevent duplicate product listings from appearing on the store when script is launched 
multiple times. If pre-existing product listing is not found, we call the `import_product()`
function that will generate JSON payload describing the product in question (with some data
cleanup) and launch a HTTP POST to the corresponding API endpoint. In both cases we must
set `X-Shopify-Access-Token` with API token we got from Shopify admin dashboard to 
authorize the request. Since this is POST request, we must check that response status
code is 201 in case it's all good.

You may notice that `time.sleep()` is called in the code to make it slower. That's because
of Shopify [rate limits](https://shopify.dev/api/admin-rest#rate_limits). We must not go
faster than two requests per seconds. That is indeed quite slow. Importing non-trivial number
of products will take some time.

Shopify also has some [client libraries](https://shopify.dev/api/admin-rest#client_libraries)
for using it's API in a few programming languages, including Python. Shopify [Python
SDK](https://shopify.github.io/shopify_python_api/) is based on [pyactiveresource](https://github.com/Shopify/pyactiveresource)
library that attempts to extend the concept of Object-Relational Mapping to RESTful APIs.
At surface, this seems like an improvement because now we have OOP API that would
allow dealing with API entities in cleaner way. Instead of constructing that JSON payload
dictionary we did before we could instantiate `Product` object and set a property for each
field. However, this library is not without its own problems. Since it calls the very same
REST API we still need to deal with slowness of data importing. Furthermore, it does not 
have a proper API session object and relies on global state fairly heavily. Currently the
documentation for this library is outdated and discusses now-deprecated way of setting
up Private App to access the API instead of the modern way we used in the code above.

Shopify also has [GraphQL API](https://shopify.dev/api/admin-graphql) with 
[bulk import process](https://shopify.dev/api/usage/bulk-operations/imports) that entails
converting data to JSONL file, uploading it to S3 bucket and calling GraphQL API to get it
processed. But that's a topic for another day.

