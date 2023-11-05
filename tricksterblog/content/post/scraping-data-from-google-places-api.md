+++
author = "rl1987"
title = "Scraping data from Google Places API"
date = "2023-11-05"
draft = true
tags = ["scraping", "osint", "python"]
+++

Google Maps Platform contains large amount of POI (Point Of Interest) data that
one might want to scrape for purposes such as lead generation, real estate
OSINT, academic research and so on. However Google Maps web/mobile apps
are highly complex pieces of software and may prove difficult to reverse engineer
for data extraction. Once could be doing some browser automation for scraping, 
but the very same POI data can be extracted through scraping the official 
[Google Places API](https://developers.google.com/maps/documentation/places/web-service/overview)
that is free to use at small scale (Google provides some free monthly credits) 
and is billed at [pay-as-you-go](https://developers.google.com/maps/documentation/places/web-service/usage-and-billing#new-payg)
model at non-trivial volumes. We will go through some basic examples of how this
data can be scraped with Python. If you retain the data for your own purposes
this still violates the [platform terms](https://cloud.google.com/maps-platform/terms), 
but it's pretty much the least shady and most convenient way to extract some of 
the data from Google Maps Platform as it relies on the official API.

Let us review what we have here to work with:

* Place Search functionality is implemented via three endpoints:
  * Find Place (`/api/place/findplacefromtext/`) to search by place name, 
    address, POI category or phone number. Fuzzy matching is applied when 
    searching.
  * Nearby Search (`/api/place/nearbysearch`) to search for places around given
    coordinates with POI filtering criteria being applied. Can be used to 
    autocomplete search queries in mobile or web apps.
  * Text Search (`/api/place/textsearch`) to search for places by arbitrary
    search queries. Can be given location and radius to bias (but not filter)
    search results.
* Place Details endpoint (`/api/place/details/`) takes `place_id` value from 
  Place Search result and provides more details about the POI including reviews,
  opening hours, photos and so on. One can apply field masks to skip on some 
  fields to improve cost and performance.
* Place Photos endpoint (`/api/place/photo`) takes a `photo_reference` from
  Place Search or Place Details response and gives you a photo rendered to given
  size preference.

In addition to that, there's two helper endpoints to assist searches via 
autocompletion.

At the time of writing Google has launched a set of next generation APIs that
you may need to enable via Google Cloud console and switch to if the old API
gets deprecated. 

For a complete list of data fields one can get, see 
[Place Data Fields](https://developers.google.com/maps/documentation/places/web-service/place-data-fields)
page. Note that business emails are not provided via Places API, but phone 
numbers and website URLs are. If API scraping is done for lead generation 
purposes, the gap could be bridged by doing opportunistic scraping of company
websites or by performing data enrichment via services like Hunter or PDL.

Place Search endpoints have one limitation that must be noted and addressed. One
search query can return at most 60 results (3 pages, 20 results each). That may
pose a problem if we want to collect non-trivial amounts of data. The solution to
this is to compute a grid of locations and run many search queries to cover the
territory.

But first we need to get the API key from Google. To proceed, you need a Google
Cloud account with billing setup completed. Follow the instructions on two Google 
Developer portal pages:

1. [Set up your Google Cloud project](https://developers.google.com/maps/documentation/places/web-service/cloud-setup)
2. [Use API Keys with Places API](https://developers.google.com/maps/documentation/places/web-service/get-api-key)

Now we have the API key. We can verify that everything works by doing a single 
request with curl:

```
$ curl -s "https://maps.googleapis.com/maps/api/place/details/json?place_id=ChIJj61dQgK6j4AR4GeTYWZsKWw&fields=id,name,international_phone_number&key=[REDACTED]" | jq
{
  "html_attributions": [],
  "result": {
    "international_phone_number": "+1 650-253-0000",
    "name": "Googleplex"
  },
  "status": "OK"
}
```

We will use the official [Google Maps Python module](https://github.com/googlemaps/google-maps-services-python) 
to benefit from the Pythonic API wrapper it provides. Furthermore, we will use the 
[`haversine`](https://github.com/mapado/haversine) module to help us 
compute a grid (since Earth is not flat the geospatial software community uses 
[Haversine formula](https://en.wikipedia.org/wiki/Haversine_formula)
that this module implements for computing distances between points on the globe).



