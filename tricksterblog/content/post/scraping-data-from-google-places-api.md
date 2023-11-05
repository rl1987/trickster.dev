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

The Python script is as follows:

```python
#!/usr/bin/python3

import csv
import configparser
import math
import os
from pprint import pprint

from haversine import haversine
import googlemaps

FIELDNAMES = ["name", "phone", "address", "website", "latitude", "longitude"]


def make_grid(gmaps_client, grid_element_side, location):
    # Search for location and get bounding box.
    # https://developers.google.com/maps/documentation/places/web-service/search-find-place

    resp = gmaps_client.find_place(location, "textquery", language="en")
    if resp.get("candidates") is None or len(resp.get("candidates")) == 0:
        print("Error: Location not found!")
        sys.exit(1)

    place_id = resp["candidates"][0]["place_id"]

    resp2 = gmaps_client.place(place_id, language="en")

    viewport = resp2.get("result", dict()).get("geometry", dict()).get("viewport")
    if viewport is None:
        print("Error: viewport not found!")
        sys.exit(2)

    from_longitude = viewport.get("southwest").get("lng")
    from_latitude = viewport.get("southwest").get("lat")
    to_longitude = viewport.get("northeast").get("lng")
    to_latitude = viewport.get("northeast").get("lat")

    print("Longitude range: {} to {}".format(from_longitude, to_longitude))
    print("Latitude range: {} to {}".format(from_latitude, to_latitude))

    horiz_len_km = haversine(
        (from_latitude, from_longitude), (from_latitude, to_longitude)
    )
    vert_len_km = haversine(
        (from_latitude, from_longitude), (to_latitude, to_longitude)
    )

    n_horiz = math.ceil(horiz_len_km / grid_element_side)
    n_vert = math.ceil(vert_len_km / grid_element_side)

    grid_elements = []

    latitude_step = (to_latitude - from_latitude) / n_vert
    longitude_step = (to_longitude - from_longitude) / n_horiz

    for i in range(n_horiz):
        for j in range(n_vert):
            south_lat = from_latitude + j * latitude_step

            north_lat = south_lat + latitude_step
            north_lat = min(north_lat, to_latitude)

            west_lng = from_longitude + i * longitude_step
            east_lng = west_lng + longitude_step
            east_lng = min(east_lng, to_longitude)

            grid_elements.append(
                "rectangle:{},{}|{},{}".format(south_lat, west_lng, north_lat, east_lng)
            )

    pprint(grid_elements)

    return grid_elements, from_latitude, to_latitude, from_longitude, to_longitude


def main():
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    config = configparser.ConfigParser()
    config.read("gplaces.ini")

    google_api_key = config["Google"]["APIKey"]
    grid_element_side = config["Google"]["GridElementSideKM"]
    grid_element_side = float(grid_element_side)

    out_f = open("gplaces.csv", "w", encoding="utf-8")

    gmaps_client = googlemaps.Client(key=google_api_key)

    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()

    location = input("Location: ")
    query = input("Search for: ")

    grid_elements, from_latitude, to_latitude, from_longitude, to_longitude = make_grid(
        gmaps_client, grid_element_side, location
    )

    seen_place_ids = set()

    # Iterate across each subregion and perform search with given query in that region
    for location_bias in grid_elements:
        resp = gmaps_client.find_place(
            query,
            "textquery",
            fields=["place_id", "name", "geometry", "formatted_address"],
            location_bias=location_bias,
            language="en",
        )
        # Iterate across search results and get contact info for each of them.
        # https://developers.google.com/maps/documentation/places/web-service/details
        for result in resp.get("candidates", []):
            place_id = result.get("place_id")
            if place_id in seen_place_ids:
                continue

            latitude = result.get("geometry").get("location").get("lat")
            longitude = result.get("geometry").get("location").get("lng")

            if latitude < from_latitude or latitude > to_latitude:
                continue

            if longitude < from_longitude or longitude > to_longitude:
                continue

            seen_place_ids.add(place_id)

            resp2 = gmaps_client.place(
                place_id,
                fields=["international_phone_number", "website"],
                language="en",
            )

            pprint(result)

            row = {
                "name": result.get("name"),
                "phone": resp2.get("result", dict()).get("international_phone_number"),
                "address": result.get("formatted_address"),
                "website": resp2.get("result", dict()).get("website"),
                "latitude": latitude,
                "longitude": longitude,
            }

            pprint(row)
            csv_writer.writerow(row)

    out_f.close()


if __name__ == "__main__":
    main()

```

When launched, this script asks to things to be entered into standard input:
location name and search query to be used with Text Search API endpoint. The
API key is found in the gplaces.ini file that is parsed with a 
`configparser` module. Location name is used to find the overall territory 
and retrieve it's bounding box in `make_grid()` function, then split the bounding
box into list of grid elements by doing some basic geometric computations. The
`make_grid()` function returns not only list of grid elements in a form that
can be used for Place Search `locationBias` parameter, but also the boundaries
of the overall bounding box for some sanity checks to be done later.

Once we have that, we can retrieve the POI data - one grid element at a time.
To remove duplicates, we keep `place_id` value in `seen_place_ids` set and
skip duplicate POIs. We also skip POIs with coordinates outside the bounding
box (remember that Text Search endpoint supports biasing, but not filtering
search results towards a given location). For each result that passes the 
filtering, we call the Place Details API (via `.place()` method of API client)
to get two additional fields: `international_phone_number` and `website`. The
resulting scraped data is written to a CSV file.
