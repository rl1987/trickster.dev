+++
author = "rl1987"
title = "Scraping data from Google Places API"
date = "2023-10-20"
draft = true
tags = ["scraping", "osint", "python"]
+++

Google Maps Platform contains large amount of POI (Point Of Interest) data that
one might want to scrape for purposes such as lead generation, real estate
OSINT, academic research and so on. However Google Maps web/mobile apps
are highly complex pieces of software and may prove difficult to reverse engineer
for data extraction. Once could go through the incovenience of doing some browser
automation for scraping, but the very same POI data can be extracted through scraping
the official [Google Places API](https://developers.google.com/maps/documentation/places/web-service/overview)
that is free for usage at small scale (Google provides some free monthly credits) 
and is billed at [pay-as-you-go](https://developers.google.com/maps/documentation/places/web-service/usage-and-billing#new-payg)
model at non-trivial volumes. We will go through some basic examples of how this
data can be scraped with Python. If you retain the data for your own purposes
this still violates the [platform terms](https://cloud.google.com/maps-platform/terms), 
but it's pretty much the least shady way and most convenient to extract some of 
the data from Google Maps Platform as it relies on the official API.

Let us review what we have here to work with.

