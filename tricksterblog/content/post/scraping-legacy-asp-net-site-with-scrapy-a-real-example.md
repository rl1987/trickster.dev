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

The site in question is [publicaccess.claytoncounty.gov](https://publicaccess.claytoncountyga.gov/search/advancedsearch.aspx?mode=sales) - 
a real estate record website for Clayton County, Georgia.
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

When we endeavor to scrape a non-trivial site we first need to do some exploration
to learn about the site so that we could strategise and plan development efforts.

If we load the site without any cookies being present in the browser we will be
redirected to disclaimer page that the county has made to cover its ass legally.
This will also give us the very first cookie with ASP.Net session ID. 

Inspecting the DOM tree reveals that pressing "Agree" button on this page would
cause a hidden form to be submitted. This form contains `__VIEWSTATE`, 
`__VIEWSTATEGENERATOR` and `__EVENTVALIDATION` fields with pre-filled valued
that deal with client session state management. We will have to submit these
values as they are without any changes when we are going to reproduce the button
press in the Scrapy spider. The same applies to our further interactions with the
site.

Pressing the "Agree" button submits the hidden form via POST requests and redirects
us to a page with some search functionality. At this point we want to get a complete
list of all the real estate property records that are available, but merely pressing
the search button on this form tells us to fill in at least one search criteria. 

In the page header there's links to other search pages. "Real Property Search" is the
default one and "Advanced Search" provides us with more options/criteria to search records
by. We will be using this one. Others are not that relevant to us. "Map Search" didn't
even work for me and "Sales Search" is similar to "Advanced Search", but with less 
stuff to search by. So we go to "Advanced Search" and try to get all records from
1900 January 1 to 2022 December 31 (it does not allow us to search earlier in time
than 1900). Note, however, that the default form is not completely useless to us - it
can be used with ID of specific parcel to check the scraped data manually since
we will not be able to fill unique URL into `source_url` field.

This did give us some search results, but not all of them as the site caps the number
of results to 10 000. This is a common problem when doing web scraping and it can 
be solved by doing search what I call search space sharding. Instead of searching for
entire recorded history, we will search in smaller increments. A little experimentation
reveals that searching for one month at a time allows each search result list to fit
within the limit of 10 000 results.

Let us go a bit deeper now. What happens when Search button is pressed? Well, we have another
form submission with bunch of crazy fields in the payload. Some of values for this form
are available in the original HTML page. Some are not and are filled by client side 
JS code instead (based on search criteria the user entered). Some can be safely ignored.
A key challenge in scraping ASP.Net sites is reproducing this kind of requests accurately
enough. We will be dealing with this later.

What if we click one of the rows in the results table? There is another POST request to
the same endpoint, but somewhat different form data being submitted. For example,
`hdLink` contains a relative link to a page we get redirected to. We don't get a unique
URL to parcel page as accessing this exact page is predicated on client state earlier
in the session and the form data in the request that happens when result row is clicked.

So where does it get the value for `hdLink` from? If we go to search results page and
inspect the row, we will find that each row (`tr` element) has `onclick` property
with JS snippet like the following:

```javascript
javascript:selectSearchRow('../Datalets/Datalet.aspx?sIndex=3&idx=1')
```

We can scrape this from HTML document and use it in our code. There will be more finer
parts of the POST request that we need to get right, but let us leave them for later.



WRITEME: developing Scrapy spider

WRITEME: splitting and parallelising the scraping
