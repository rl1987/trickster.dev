+++
author = "rl1987"
title = "Scraping legacy ASP.Net sites with Scrapy: a real world example"
date = "2022-10-31"
draft = true
tags = ["web-scraping", "python", "scrapy"]
+++

Legacy ASP.Net sites are some of the most difficult ones to deal with for web scraper
developers due to their archaic state management mechanism that entails hidden form
submissions via POST requests. This stuff is not easy to reproduce programmatically.
In this post we will discuss a real world example of scraping a site based on some old
version of ASP.Net technology. 

The site in question is [publicaccess.claytoncounty.gov](https://publicaccess.claytoncountyga.gov/search/advancedsearch.aspx?mode=sales).
Our objective is to scrape all the real estate sales records from this site (fun fact:
there's plenty of juicy data various branches of US government publish on
official sites that can be scraped and monetised). We will be using Scrapy framework.
It is assumed that the reader is already familiar with this framework, thus some of
the basic technical details will be skipped. Data we want to scrape will correspond
to the following subclass of `scrapy.Item`:

```python
class SalesItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    state = scrapy.Field()
    property_zip5 = scrapy.Field()
    property_street_address = scrapy.Field()
    property_city = scrapy.Field()
    property_county = scrapy.Field()
    property_id = scrapy.Field()
    sale_datetime = scrapy.Field()
    property_type = scrapy.Field()
    sale_price = scrapy.Field()
    seller_1_name = scrapy.Field()
    buyer_1_name = scrapy.Field()
    building_num_units = scrapy.Field()
    building_year_built = scrapy.Field()
    source_url = scrapy.Field()
    book = scrapy.Field()
    page = scrapy.Field()
    transfer_deed_type = scrapy.Field()
    property_township = scrapy.Field()
    property_lat = scrapy.Field()
    property_lon = scrapy.Field()
    sale_id = scrapy.Field()
    deed_date = scrapy.Field()
    building_num_stories = scrapy.Field()
    building_num_beds = scrapy.Field()
    building_num_baths = scrapy.Field()
    building_area_sqft = scrapy.Field()
    building_assessed_value = scrapy.Field()
    building_assessed_date = scrapy.Field()
    land_area_acres = scrapy.Field()
    land_area_sqft = scrapy.Field()
    land_assessed_value = scrapy.Field()
    seller_2_name = scrapy.Field()
    buyer_2_name = scrapy.Field()
    land_assessed_date = scrapy.Field()
    seller_1_state = scrapy.Field()
    seller_2_state = scrapy.Field()
    buyer_1_state = scrapy.Field()
    buyer_2_state = scrapy.Field()
    total_assessed_value = scrapy.Field()
    total_appraised_value = scrapy.Field()
    land_appraised_value = scrapy.Field()
    building_appraised_value = scrapy.Field()
    land_type = scrapy.Field()
```

We don't need to fill all the fields here, just the ones that are available from
the source website.

WRITEME: exploring the site

WRITEME: developing Scrapy spider

WRITEME: splitting and parallelising the scraping
