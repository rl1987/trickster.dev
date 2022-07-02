+++
author = "rl1987"
title = "How to scrape Zillow with Python and Scrapy"
date = "2022-07-02"
draft = true
tags = ["web-scraping", "python", "scrapy"]
+++

For North America, Zillow is a number one portal for real estate listings for sale and rent.
Due to its significance in real estate industry it is of interest for web scraping. We
are going to use Python programming language and Scrapy framework to scrape information
on various properties on Zillow. Let us assume that FSBO (for sale by owner) listings
are of particular interest to us. They are sold directly by the owner and represent
a business opportunity for realtor to help them make a sale.

Before we write a first of code, we need to explore the site to plan a general strategy
of how we are going to scrape it. We want to take a look how site handles cookies so
we force-delete them from the browser to see how they are acquired in the request flow.

[TODO: Screenshot 1]

On the top header we see options to rent, buy, sell, etc. If we hover the word "Buy" with
mouse cursor we can choose properties that are sold by the owner. We click this link with
DevTools being open.

[TODO: Screenshots]

Now if we enter some location into search bar we only get the FSBO listings, but there's 
nothing in the URL that seems to tell the site to only return such results. This suggests
that cookies are being used for session management and to keep track of state between
requests. Let us look bit deeper into this.

By scrolling up in the Network tab of DevTools panel we find the request that was sent 
when we clicked the "For Sale By Owner" link earlier. In response, Zillow gives us some
cookies, one of which is named `search` and has letters `fsbo` in the value.

However's there a bit of a problem. Search results table has two tabs. The first one which
is on by default is for results that already have real estate agent helping with the 
sale and we are actually interested in results on the second tab. Let us see what happens
when we switch the tab. We find that API request is made when we switch the tab to update
the data being shown.

[TODO: screenshot]

There are two key parameters to this request. One is for search query state that contains
geographical boundaries and other search criteria. Another specifies which result category
we want to get. Both are serialised as JSON strings. Response payload contains data about
properties being found in JSON format. We are talking to a private API here.

If we click on one of the search results we see that few more API requests are made. One 
of them is of particular interest to us. There's a request sent to `/graphql` endpoint
having `ForSaleShopperPlatformFullRenderQuery` value for URL parameter `operationName`.
In the response there's bunch of data that is rendered into property details page, 
including contact details for a person trying to sell their place. This request is 
parametrised not only by URL paramers, but there's also JSON payload with Zillow 
property ID and operation name. We will be reproducing this request programmatically, as
well as the previous one that gives us search results.

To start sending search API requests we need to need to generate or extract the 
`searchQueryState` parameter. Turns out, it is available in the HTML of search results
page, assuming it was requested with the proper cookies.

So the general strategy for scraping Zillow is the following:
1. We reproduce the HTTP request for choosing FSBO listings so that proper cookies
would be received by our code.
2. Load the first (HTML) page of search results to extract the search query state.
3. We iterate across all pages of search results by updating the part of search
query state that deals with pagination.
4. We extract the relevant parts from property detail API response and save them 
to output file. We also download property images.

In summary, we will be using a hybrid approach that starts with scraping a small 
piece of information from HTML page to bootstrap private API scraping.



