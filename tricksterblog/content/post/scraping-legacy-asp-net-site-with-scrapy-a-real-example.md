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

[Screenshot 1](/2022-10-11_16.57.02.png)

Inspecting the DOM tree reveals that pressing "Agree" button on this page would
cause a hidden form to be submitted. This form contains `__VIEWSTATE`, 
`__VIEWSTATEGENERATOR` and `__EVENTVALIDATION` fields with pre-filled valued
that deal with client session state management. We will have to submit these
values as they are without any changes when we are going to reproduce the button
press in the Scrapy spider. The same applies to our further interactions with the
site.

[Screenshot 2](/2022-10-11_16.58.27.png)

Pressing the "Agree" button submits the hidden form via POST requests and redirects
us to a page with some search functionality. At this point we want to get a complete
list of all the real estate property records that are available, but merely pressing
the search button on this form tells us to fill in at least one search criteria. 

[Screenshot 3](/2022-10-11_17.04.07.png)

In the page header there's links to other search pages. "Real Property Search" is the
default one and "Advanced Search" provides us with more options/criteria to search records
by. We will be using this one. Others are not that relevant to us. "Map Search" didn't
even work for me and "Sales Search" is similar to "Advanced Search", but with less 
stuff to search by. So we go to "Advanced Search" and try to get all records from
1900 January 1 to 2022 December 31 (it does not allow us to search earlier in time
than 1900). Note, however, that the default form is not completely useless to us - it
can be used with ID of specific parcel to check the scraped data manually since
we will not be able to fill unique URL into `source_url` field.

[Screenshot 4](/2022-10-11_17.16.37.png)

This did give us some search results, but not all of them as the site caps the number
of results to 10 000. This is a common problem when doing web scraping and it can 
be solved by doing search what I call search space sharding. Instead of searching for
entire recorded history, we will search in smaller increments. A little experimentation
reveals that searching for one month at a time allows each search result list to fit
within the limit of 10 000 results.

[Screenshot 5](/2022-10-11_17.23.04.png)

Let us go a bit deeper now. What happens when Search button is pressed? Well, we have another
form submission with bunch of crazy fields in the payload. Some of values for this form
are available in the original HTML page. Some are not and are filled by client side 
JS code instead (based on search criteria the user entered). Some can be safely ignored.
A key challenge in scraping ASP.Net sites is reproducing this kind of requests accurately
enough. We will be dealing with this later.

[Screenshot 6](/2022-10-11_17.26.25.png)

What if we click one of the rows in the results table? There is another POST request to
the same endpoint, but somewhat different form data being submitted. For example,
`hdLink` contains a relative link to a page we get redirected to. We don't get a unique
URL to parcel page as accessing this exact page is predicated on client state earlier
in the session and the form data in the request that happens when result row is clicked.

[Screenshot 7](/2022-10-11_17.41.25.png)

So where does it get the value for `hdLink` from? If we go to search results page and
inspect the row, we will find that each row (`tr` element) has `onclick` property
with JS snippet like the following:

```javascript
javascript:selectSearchRow('../Datalets/Datalet.aspx?sIndex=3&idx=1')
```

[Screenshot 8](/2022-10-11_17.43.10.png)

We can scrape this from HTML document and use it in our code. There will be more finer
parts of the POST request that we need to get right, but let us leave them for later.

When we go see the result we find that data about parcel is broken down across several 
pages. The first page we get is "Tax Commisioner Summary" page that contains some
information on property address, most common owner, property class and so on. There
are links on the side to further pages (no hidden forms this time, but we're not
getting unique URLs either). 

[Screenshot 9](/2022-10-11_18.09.27.png)

We will be scraping these pages:

* "Tax Commissioner Summary" for `property_id`, `property_street_address` and
`property_type` fields.
* "Residential" - `building_year_built`, `building_num_beds`, `building_num_baths`.
* "Value History" - assessed/appraised monetary values (land, buildings and total).
We will need to make sure that the year of appraisal/assessment matches that of a
sale for each row we output.
* "Land" - `land_area_acres`, `land_area_sqft`.
* "Sales" - everything about parcel sale: `sale_datetime`, `sale_price`, `seller_1_name`,
`buyer_1_name`, `seller_2_name`, `buyer_2_name`, `book`, `page` and `transfer_deed_type`.

There's one sale per page, but sale pages form a linked list through the little navigation
links that we can use. 

[Screenshot 10](/2022-10-11_18.23.35.png)

The same applies to parcels - there's a way to navigate between adjacent search results
(based on form submission this time - we will need to work out details here).

[Screenshot 11](/2022-10-11_18.24.56.png)

This lets us have a linear flow between pages without the inconvenience of backtracking.

Based on what we learned so far the scraping strategy will be as follows:

* Shard search space by searching for one month worth of results per search query.
  * For each search, go to the first result (reproduce form submission).
    * Scrape data from "Tax Commisioner Summary", "Residential", "Value History", "Land"
      pages. Use `meta` dictionary to pass information between requests so that stuff
      is being scraped incrementally.
    * Scrape sales data by traversing linked list of sales records. Create items here by
      filling stuff from sales record and stuff from earlier. Make sure that appraised/
      assessed values match the sales year. Refrain from including them if it's not
      possible.
  * Go to next parcel so that list of parcels is traversed to the end.

Due to the nature of legacy ASP.Net technology we cannot benefit much from built-in 
concurrency of Scrapy at session level - we risk messing up the session if we don't
load pages one at a time. However we can have multiple sessions at the same time - we
will be writing some extra code to make the scraping faster and more reliable.

Let us go through the Scrapy spider code now, one step at a time. 

We start scraping by loading the disclaimer page (this will give us the ASP.Net session cookie)
and reproducing the action of user pressing the "Agree" button:

```python
import scrapy

from scrapy.http import FormRequest

class ClaytonSpider(scrapy.Spider):
    name = "clayton"
    allowed_domains = ["publicaccess.claytoncountyga.gov"]
    start_urls = [
        "https://publicaccess.claytoncountyga.gov/Search/Disclaimer.aspx?FromUrl=../search/advancedsearch.aspx?mode=advanced",
        "https://publicaccess.claytoncountyga.gov/search/advancedsearch.aspx?mode=advanced",
    ]
    start_year = 1939
    state = "GA"
    county = "CLAYTON"
    shards = []

    def start_requests(self):
        yield scrapy.Request(self.start_urls[0], callback=self.parse_disclaimer_page)

    def parse_disclaimer_page(self, response):
        yield FormRequest.from_response(
            response,
            formxpath='//form[@name="Form1"]',
            clickdata={"name": "btAgree"},
            callback=self.parse_form_page,
        )
```

In this case we are able to use `from_response` utility method of `FormRequest` class.

We have skipped this part for now, but `shards` list will be filled with year-month tuples
to be used in search step.

Callback to request that submits the agreement to legal terms is `parse_form_page()`:

```python
    def parse_form_page(self, response):
        if len(self.shards) == 0:
            yield None
            return

        year, month = self.shards.pop()
        logging.info("Year: {}, month: {}".format(year, month))

        days_in_month = calendar.monthrange(year, month)[1]

        start_date = date(year=year, month=month, day=1)
        end_date = date(year=year, month=month, day=days_in_month)

        yield self.make_search_form_request(response, start_date, end_date)
```

Now we have a form we can fill, thus we remove one search shard from the list and use it to
fill the search form. Since we will be doing this a lot, we have another method for this 
purpose:

```python
    def make_search_form_request(self, response, start_date, end_date):
        start_date_str = self.stringify_date(start_date)
        end_date_str = self.stringify_date(end_date)

        form_data = self.extract_form(response, '//form[@name="frmMain"]')

        form_data["hdCriteria"] = "salesdate|{}~{}".format(start_date_str, end_date_str)
        form_data["ctl01$cal1"] = start_date.isoformat()
        form_data["ctl01$cal1$dateInput"] = start_date_str
        form_data["txtCrit"] = start_date_str
        form_data["ctl01$cal2"] = end_date.isoformat()
        form_data["ctl01$cal2$dateInput"] = end_date_str
        form_data["txtCrit2"] = end_date_str
        form_data["PageNum"] = "1"
        form_data["PageSize"] = "1"
        form_data["hdCriteriaTypes"] = "N|N|C|C|C|N|C|C|N|D|N|N|C|C|C|N|N"
        form_data["sCriteria"] = "0"

        logging.debug(form_data)

        return FormRequest(
            response.url,
            formdata=form_data,
            callback=self.parse_search_result_list,
            dont_filter=True,
        )

```

You can see that it calls a helper method to extract form fields already present in the
page, but also fills bunch of fields explicitly. This is significant. How do I know that 
these form fields have to be filled in this exact way? Well, through experimentation, 
persistance and plain old paying the fucking attention. It took me quite a bit of effort to
work these exact details out, but there was nothing magical or secret in doing that. There
was multiple takes of painstakingly comparing what `logging.debug()` logs out with what I 
see in the Chrome dev tools until I got it working correctly.

Next, we get to parse the HTML page with result list:

```python
    def parse_search_result_list(self, response):
        first_row = response.xpath('//tr[@class="SearchResults"][1]')
        if len(first_row) != 1:
            yield scrapy.Request(
                self.start_urls[-1], callback=self.parse_form_page, dont_filter=True
            )
            return

        logging.debug(first_row.xpath(".//text()").getall())

        onclick = first_row.attrib.get("onclick")
        rel_url = onclick.replace("javascript:selectSearchRow('", "").replace("')", "")

        form_data = self.extract_form(response, '//form[@name="frmMain"]')
        form_data["hdLink"] = rel_url
        form_data["hdAction"] = "Link"
        form_data["hdSelectAllChecked"] = "false"
        form_data["sCriteria"] = "0"
        logging.debug(form_data)

        action = response.xpath('//form[@name="frmMain"]/@action').get()
        form_url = urljoin(response.url, action)

        yield FormRequest(
            form_url,
            formdata=form_data,
            callback=self.parse_property_main_page,
            dont_filter=True,
        )
```

We try to extract the first row of the results table. If it's not there we take it that there's
no records for the given month, thus we move on to the next shard in the list. If it is there,
we extract `onclick` property, do some basic string manipulation to extract the relative link
from that, fill the hidden form and submit it. This will give us a parcel summary page on the
next callback. 

The next callback is `parse_property_main_page()`:

```python
    def parse_property_main_page(self, response):
        parid = response.xpath('//input[@id="hdXPin"]/@value').get()
        property_street_address = (
            response.xpath('//td[@class="DataletHeaderBottom"][last()]/text()')
            .get("")
            .strip()
        )
        property_street_address = " ".join(
            property_street_address.split()
        )  # https://stackoverflow.com/a/1546251

        item = SalesItem()
        item["state"] = self.state
        item["property_id"] = parid
        item["property_street_address"] = property_street_address
        item["property_county"] = self.county
        item["property_type"] = response.xpath(
            '//tr[./td[contains(text(),"Property Class")]]/td[@class="DataletData"]/text()'
        ).get()

        residential_link = response.xpath(
            '//a[./span[text()="Residential"]]/@href'
        ).get()
        yield response.follow(
            residential_link,
            meta={"item": item},
            callback=self.parse_property_residential_page,
            dont_filter=True,
        )

```

Here we do some XPath queries to extract some fields into newly created item object. We also
extract link to "Residential" page and go there. Since we're not done filling the item, we
pass it along the request by using the meta dictionary. 

At next callback we scrape the "Residential" page:

```python
    def parse_property_residential_page(self, response):
        item = response.meta.get("item")

        parid = response.xpath('//input[@id="hdXPin"]/@value').get()
        assert parid == item["property_id"]

        item["building_year_built"] = response.xpath(
            '//tr[./td[text()="Year Built"]]/td[@class="DataletData"]/text()'
        ).get()
        item["building_num_beds"] = response.xpath(
            '//tr[./td[text()="Bedrooms"]]/td[@class="DataletData"]/text()'
        ).get()
        item["building_num_baths"] = response.xpath(
            '//tr[./td[text()="Full Baths"]]/td[@class="DataletData"]/text()'
        ).get()

        value_history_link = response.xpath(
            '//a[./span[text()="Value History"]]/@href'
        ).get()
        yield response.follow(
            value_history_link,
            meta={"item": item},
            callback=self.parse_property_value_history_page,
            dont_filter=True,
        )

```

We get the item object from `response.meta`, fill in some more fields and pass it along the 
next request that will fetch us "Value History" page that we parse at next callback:

```python
    def parse_property_value_history_page(self, response):
        item = response.meta.get("item")
        appr_rows = response.meta.get("appr_rows")
        as_rows = response.meta.get("as_rows")

        appr_rows = dict()
        appr_header = None

        appr_values_table = response.xpath('//table[@id="Appraised Values"]')
        if appr_values_table is not None:
            for row in appr_values_table.xpath("./tr"):
                row = row.xpath("./td/text()").getall()
                if appr_header is None:
                    appr_header = row
                    continue

                if len(row) == 0:
                    continue

                year = row[0]
                try:
                    year = int(year)
                except:
                    continue
                row = dict(zip(appr_header, row))
                appr_rows[year] = row

        logging.debug(appr_rows)

        as_rows = dict()
        as_header = None

        as_values_table = response.xpath('//table[@id="Assessed Values"]')
        if as_values_table is not None:
            for row in as_values_table.xpath("./tr"):
                row = row.xpath("./td/text()").getall()
                if as_header is None:
                    as_header = row
                    continue

                if len(row) == 0:
                    continue

                year = row[0]
                try:
                    year = int(year)
                except:
                    continue
                row = dict(zip(as_header, row))
                as_rows[year] = row

        logging.debug(as_rows)

        meta_dict = {"item": item, "appr_rows": appr_rows, "as_rows": as_rows}

        land_link = response.xpath('//a[./span[text()="Land"]]/@href').get()
        yield response.follow(
            land_link,
            meta=meta_dict,
            callback=self.parse_property_land_page,
            dont_filter=True,
        )
```

Now we have two tables. One for assessed values and one for appraised values (these are different
ways to evaluate real estate prices). In each row there will be year and numbers for land, building
and overall value. For some parcels these tables will be missing, which means we have to 
gracefully skip this page without crashing the scraping job. So what we do is look for tables
via XPath queries, scrape their rows and store the results in dictionaries indexed by years.
Since this data will be needed later we pass it along the request through meta dictionary.

[Screenshot 12](/2022-10-11_18.16.50.png)

At next callback, "Land" page is scraped:

```python
    def parse_property_land_page(self, response):
        item = response.meta.get("item")
        appr_rows = response.meta.get("appr_rows")
        as_rows = response.meta.get("as_rows")

        item["land_area_acres"] = (
            response.xpath('//tr[./td[text()="Acres"]]/td[@class="DataletData"]/text()')
            .get("")
            .replace("\xa0", "")
        )
        if item["land_area_acres"].startswith("."):
            item["land_area_acres"] = 0
        elif item["land_area_acres"] != "":
            item["land_area_acres"] = round(float(item["land_area_acres"]))
        item["land_area_sqft"] = (
            response.xpath(
                '//tr[./td[text()="Square Feet"]]/td[@class="DataletData"]/text()'
            )
            .get("")
            .replace("\xa0", "")
            .replace(",", "")
        )
        item["land_type"] = response.xpath(
            '//tr[./td[text()="Land Type"]]/td[@class="DataletData"]/text()'
        ).get()

        meta_dict = {"item": item, "appr_rows": appr_rows, "as_rows": as_rows}

        sales_link = response.xpath('//a[./span[text()="Sales"]]/@href').get()
        yield response.follow(
            sales_link,
            meta=meta_dict,
            callback=self.parse_property_sales_page,
            dont_filter=True,
        )
```

We extract some more fields into the item object and go to the "Sales" page, like we did
in previous steps. Note that `meta` dictionary has to be recreated like it is being done here.
One cannot take a reference to `meta` from response object, change something it a bit and pass
it into new request object, as Scrapy framework also sets some key-value pairs in this 
dictionary for internal use. Not recreating the meta dictionary will mess up the Scrapy internals.

So finally we get to scrape the sales data at in `parse_property_sales_page()`:

```python
    def parse_property_sales_page(self, response):
        item = response.meta.get("item")
        appr_rows = response.meta.get("appr_rows")
        as_rows = response.meta.get("as_rows")

        sale_date_str = response.xpath(
            '//tr[./td[text()="Sale Date"]]/td[@class="DataletData"]/text()'
        ).get()
        if sale_date_str is not None:
            sale_date_str = parse_datetime(sale_date_str).isoformat().replace("T", " ")

        item["sale_datetime"] = sale_date_str
        item["sale_price"] = (
            response.xpath(
                '//tr[./td[text()="Sale Price"]]/td[@class="DataletData"]/text()'
            )
            .get("")
            .replace("$", "")
            .replace(",", "")
        )
        item["seller_1_name"] = (
            response.xpath(
                '//tr[./td[text()="Grantor"]]/td[@class="DataletData"]/text()'
            )
            .get("")
            .replace("\xa0", "")
        )
        item["buyer_1_name"] = (
            response.xpath(
                '//tr[./td[text()="Grantee"]]/td[@class="DataletData"]/text()'
            )
            .get("")
            .replace("\xa0", "")
        )
        item["seller_2_name"] = (
            response.xpath(
                '//tr[./td[text()="Grantor 2"]]/td[@class="DataletData"]/text()'
            )
            .get("")
            .replace("\xa0", "")
        )
        item["buyer_2_name"] = (
            response.xpath(
                '//tr[./td[text()="Grantee 2"]]/td[@class="DataletData"]/text()'
            )
            .get("")
            .replace("\xa0", "")
        )
        item["book"] = response.xpath(
            '//tr[./td[text()="Deed Book"]]/td[@class="DataletData"]/text()'
        ).get()
        item["page"] = response.xpath(
            '//tr[./td[text()="Deed Page"]]/td[@class="DataletData"]/text()'
        ).get()
        item["transfer_deed_type"] = response.xpath(
            '//tr[./td[text()="Instrument Type"]]/td[@class="DataletData"]/text()'
        ).get()
        item[
            "source_url"
        ] = "https://publicaccess.claytoncountyga.gov/search/advancedsearch.aspx?mode=advanced"

        appr_row = appr_rows.get(sale_date.year)
        if appr_row is not None:
            item["total_appraised_value"] = appr_row.get("Total", "").replace(",", "")
            item["land_appraised_value"] = appr_row.get("Land", "").replace(",", "")
            item["building_appraised_value"] = appr_row.get("Building", "").replace(
                ",", ""
            )
        else:
            item["total_appraised_value"] = None
            item["land_appraised_value"] = None
            item["building_appraised_value"] = None

        as_row = as_rows.get(sale_date.year)
        if as_row is not None:
            item["building_assessed_value"] = as_row.get("Buidling", "").replace(
                ",", ""
            )
            item["building_assessed_date"] = sale_date.year
            item["land_assessed_value"] = as_row.get("Land", "").replace(",", "")
            item["total_assessed_value"] = as_row.get("Total", "").replace(",", "")
        else:
            item["building_assessed_value"] = None
            item["building_assessed_value"] = None
            item["land_assessed_value"] = None
            item["total_assessed_value"] = None

        yield item
```

Again, nothing particularly fancy here. Just doing XPath queries and string manipulation to fill
some more fields in the item object. We also access the assessed/appraised value dictionaries
we created earlier to fill the relevant numbers for the same year as the sale (if possible).

But there's more. We also have to traverse to next page, to get data for next sale.

```python
        next_sale_link = response.xpath(
            '//a[./i[@class="icon-angle-right "]]/@href'
        ).get()
        if next_sale_link is not None:
            yield response.follow(
                next_sale_link,
                callback=self.parse_property_sales_page,
                dont_filter=True,
                meta={"item": item},
            )
            return
```

We extract the link to next sale and follow it. But why did we do `return` after yielding
the new request? Well, that's because at this point we merely want to go the page of next sale
record. Further in the method we have code that does form submission to go the summary page
of next parcel, so this entire shebang can be done again for next property:

```python
        to_from_input_text = response.xpath(
            '//input[@name="DTLNavigator$txtFromTo"]/@value'
        ).get()
        idx, total = to_from_input_text.split(" of ")
        idx = int(idx)
        total = int(total)

        if idx == total:
            yield scrapy.Request(
                self.start_urls[-1],
                callback=self.parse_form_page,
                dont_filter=True,
                meta={"item": item},
            )
            return

        form_data = self.extract_form(response, '//form[@name="frmMain"]')
        del form_data["DTLNavigator$imageNext"]
        del form_data["DTLNavigator$imageLast"]
        form_data["DTLNavigator$imageNext.x"] = "0"  # XXX
        form_data["DTLNavigator$imageNext.y"] = str(idx + 1)
        form_data["hdMode"] = "DEK_PROFILE"
        logging.info(form_data)

        action = response.xpath('//form[@name="frmMain"]/@action').get()
        form_url = urljoin(response.url, action).replace(
            "mode=sales", "mode=dek_profile"
        )

        yield FormRequest(
            form_url,
            formdata=form_data,
            callback=self.parse_property_main_page,
            dont_filter=True,
        )
``` 

We take care to modify URL and `hdMode` field to make it go to the summary page, not the "Sales"
page. We also address the possibility of the current parcel being the last in the list, which
would warrant going to the next scheduled search space shard.

You can notice that requests tend to be instantiated with `dont_filter` flag. This is because
site being scraped does not have unique URLs for many pages, which would trigger Scrapy 
deduplication mechanism needlessly, thus cancelling the scraping job before it was properly
finished.

One more thing I would like to explain is how the scraping was parallelised to allow running
multiple client sessions in parallel and retry the search shard scraping if needed.
The spider has the following contstructor method:

```python
    def __init__(self, year=None, month=None, stats_filepath=None):
        super().__init__()

        self.stats_filepath = stats_filepath

        if year is not None and month is not None:
            year = int(year)
            month = int(month)
            self.shards = [(year, month)]
            return

        for year in range(self.start_year, datetime.today().year + 1):
            for month in range(1, 13):
                shard = (year, month)
                self.shards.append(shard)

```

If year and month values are provided through Scrapy CLI it will plan to scrape a single
month worth of data. Otherwise, it will plan to scrape the entire data, one month at a time.
How does this help us? Well, there is a helper script that will launch bunch of Scrapy processes
in parallel and retry them if needed (based on some error conditions that may happen due to
site instability):

```python
#!/usr/bin/python3

import multiprocessing
import logging
import subprocess
import json
import os
import sys

spider_name = None


def run_scrapy_subprocess(year, month):
    csv_filename = "{}-{}-{}.csv".format(spider_name, year, month)
    if os.path.isfile(csv_filename):
        os.unlink(csv_filename)

    log_filename = "scrapy-{}-{}.log".format(year, month)
    if os.path.isfile(log_filename):
        os.unlink(log_filename)

    stats_filename = "stats-{}-{}.json".format(year, month)

    cmd = [
        "scrapy",
        "runspider",
        "-o",
        csv_filename,
        "--logfile",
        log_filename,
        "housingprices/spiders/{}.py".format(spider_name),
        "-a",
        "year={}".format(year),
        "-a",
        "month={}".format(month),
        "-a",
        "stats_filepath={}".format(stats_filename),
    ]

    print(cmd)

    result = subprocess.run(cmd)
    if result.returncode != 0:
        return False

    json_f = open(stats_filename, "r")
    stats = json.load(json_f)
    json_f.close()

    if stats.get("log_count/ERROR") is not None:
        return False

    if (
        stats.get("downloader/response_status_count/500") is not None
        and stats.get("downloader/response_status_count/500") > 8
    ):
        return False

    if (
        stats.get("downloader/response_status_count/501") is not None
        and stats.get("downloader/response_status_count/501") > 8
    ):
        return False

    return True


def perform_task(shard):
    year, month = shard
    print("Year: {}, month: {}".format(year, month))

    while True:
        success = run_scrapy_subprocess(year, month)
        if success:
            print("{} {} succeeded".format(year, month))
            break

        print("{} {} failed - retrying".format(year, month))


def main():
    global spider_name

    if len(sys.argv) != 2:
        print("Usage:")
        print("{} <spider_name>".format(sys.argv[0]))
        return

    spider_name = sys.argv[1]

    shards = []

    from_year = 1901
    to_year = 2022

    for year in range(from_year, to_year + 1):
        for month in range(1, 13):
            shard = (year, month)
            shards.append(shard)

    pool = multiprocessing.Pool(32)
    pool.map(perform_task, shards)


if __name__ == "__main__":
    main()

```

I was running this on VPS inside tmux session to perform the scraping. One thing you may
notice is that it sets `stats_filepath` to file name unique to scraping job and read JSON from
this file to check if scraping has succceeded. This requires some setup in Scrapy project.
One thing we need is following piece of code to save the scraping stats when spider is done
scraping:

```python
# Based on:
# https://stackoverflow.com/questions/61402939/scrapy-how-to-save-crawling-statistics-to-json-file

from scrapy.statscollectors import StatsCollector
from scrapy.utils.serialize import ScrapyJSONEncoder


class MyStatsCollector(StatsCollector):
    def _persist_stats(self, stats, spider):
        encoder = ScrapyJSONEncoder()

        filename = "stats.json"
        if spider.stats_filepath is not None:
            filename = spider.stats_filepath

        out_f = open(filename, "w")
        data = encoder.encode(stats)
        out_f.write(data)
        out_f.close()

```

This has to be enabled in the settings as the linked Stack Overflow answer describes.

To sum it up, a complete Scrapy spider code is as follows:

```python
import scrapy

from scrapy.http import FormRequest
from dateutil.parser import parse as parse_datetime

import calendar
from datetime import datetime, date
import logging
from urllib.parse import urljoin

from housingprices.items import SalesItem


class ClaytonSpider(scrapy.Spider):
    name = "clayton"
    allowed_domains = ["publicaccess.claytoncountyga.gov"]
    start_urls = [
        "https://publicaccess.claytoncountyga.gov/Search/Disclaimer.aspx?FromUrl=../search/advancedsearch.aspx?mode=advanced",
        "https://publicaccess.claytoncountyga.gov/search/advancedsearch.aspx?mode=advanced",
    ]
    start_year = 1939
    state = "GA"
    county = "CLAYTON"
    shards = []
    stats_filepath = None

    def __init__(self, year=None, month=None, stats_filepath=None):
        super().__init__()

        self.stats_filepath = stats_filepath

        if year is not None and month is not None:
            year = int(year)
            month = int(month)
            self.shards = [(year, month)]
            return

        for year in range(self.start_year, datetime.today().year + 1):
            for month in range(1, 13):
                shard = (year, month)
                self.shards.append(shard)

    def start_requests(self):
        yield scrapy.Request(self.start_urls[0], callback=self.parse_disclaimer_page)

    def parse_disclaimer_page(self, response):
        yield FormRequest.from_response(
            response,
            formxpath='//form[@name="Form1"]',
            clickdata={"name": "btAgree"},
            callback=self.parse_form_page,
        )

    def stringify_date(self, d):
        return "{:02d}/{:02d}/{:04d}".format(d.month, d.day, d.year)

    def extract_form(self, response, form_xpath):
        form_data = dict()

        for hidden_input in response.xpath(form_xpath).xpath(".//input"):
            name = hidden_input.attrib.get("name")
            if name is None:
                continue
            value = hidden_input.attrib.get("value")
            if value is None:
                value = ""

            form_data[name] = value

        return form_data

    def make_search_form_request(self, response, start_date, end_date):
        start_date_str = self.stringify_date(start_date)
        end_date_str = self.stringify_date(end_date)

        form_data = self.extract_form(response, '//form[@name="frmMain"]')

        form_data["hdCriteria"] = "salesdate|{}~{}".format(start_date_str, end_date_str)
        form_data["ctl01$cal1"] = start_date.isoformat()
        form_data["ctl01$cal1$dateInput"] = start_date_str
        form_data["txtCrit"] = start_date_str
        form_data["ctl01$cal2"] = end_date.isoformat()
        form_data["ctl01$cal2$dateInput"] = end_date_str
        form_data["txtCrit2"] = end_date_str
        form_data["PageNum"] = "1"
        form_data["PageSize"] = "1"
        form_data["hdCriteriaTypes"] = "N|N|C|C|C|N|C|C|N|D|N|N|C|C|C|N|N"
        form_data["sCriteria"] = "0"

        logging.debug(form_data)

        return FormRequest(
            response.url,
            formdata=form_data,
            callback=self.parse_search_result_list,
            dont_filter=True,
        )

    def parse_form_page(self, response):
        if len(self.shards) == 0:
            yield None
            return

        year, month = self.shards.pop()
        logging.info("Year: {}, month: {}".format(year, month))

        days_in_month = calendar.monthrange(year, month)[1]

        start_date = date(year=year, month=month, day=1)
        end_date = date(year=year, month=month, day=days_in_month)

        yield self.make_search_form_request(response, start_date, end_date)

    def parse_search_result_list(self, response):
        first_row = response.xpath('//tr[@class="SearchResults"][1]')
        if len(first_row) != 1:
            yield scrapy.Request(
                self.start_urls[-1], callback=self.parse_form_page, dont_filter=True
            )
            return

        logging.debug(first_row.xpath(".//text()").getall())

        onclick = first_row.attrib.get("onclick")
        rel_url = onclick.replace("javascript:selectSearchRow('", "").replace("')", "")

        form_data = self.extract_form(response, '//form[@name="frmMain"]')
        form_data["hdLink"] = rel_url
        form_data["hdAction"] = "Link"
        form_data["hdSelectAllChecked"] = "false"
        form_data["sCriteria"] = "0"
        logging.debug(form_data)

        action = response.xpath('//form[@name="frmMain"]/@action').get()
        form_url = urljoin(response.url, action)

        yield FormRequest(
            form_url,
            formdata=form_data,
            callback=self.parse_property_main_page,
            dont_filter=True,
        )

    def parse_property_main_page(self, response):
        parid = response.xpath('//input[@id="hdXPin"]/@value').get()
        property_street_address = (
            response.xpath('//td[@class="DataletHeaderBottom"][last()]/text()')
            .get("")
            .strip()
        )
        property_street_address = " ".join(
            property_street_address.split()
        )  # https://stackoverflow.com/a/1546251

        item = SalesItem()
        item["state"] = self.state
        item["property_id"] = parid
        item["property_street_address"] = property_street_address
        item["property_county"] = self.county
        item["property_type"] = response.xpath(
            '//tr[./td[contains(text(),"Property Class")]]/td[@class="DataletData"]/text()'
        ).get()

        residential_link = response.xpath(
            '//a[./span[text()="Residential"]]/@href'
        ).get()
        yield response.follow(
            residential_link,
            meta={"item": item},
            callback=self.parse_property_residential_page,
            dont_filter=True,
        )

    def parse_property_residential_page(self, response):
        item = response.meta.get("item")

        parid = response.xpath('//input[@id="hdXPin"]/@value').get()
        assert parid == item["property_id"]

        item["building_year_built"] = response.xpath(
            '//tr[./td[text()="Year Built"]]/td[@class="DataletData"]/text()'
        ).get()
        item["building_num_beds"] = response.xpath(
            '//tr[./td[text()="Bedrooms"]]/td[@class="DataletData"]/text()'
        ).get()
        item["building_num_baths"] = response.xpath(
            '//tr[./td[text()="Full Baths"]]/td[@class="DataletData"]/text()'
        ).get()

        value_history_link = response.xpath(
            '//a[./span[text()="Value History"]]/@href'
        ).get()
        yield response.follow(
            value_history_link,
            meta={"item": item},
            callback=self.parse_property_value_history_page,
            dont_filter=True,
        )

    def parse_property_value_history_page(self, response):
        item = response.meta.get("item")
        appr_rows = response.meta.get("appr_rows")
        as_rows = response.meta.get("as_rows")

        appr_rows = dict()
        appr_header = None

        appr_values_table = response.xpath('//table[@id="Appraised Values"]')
        if appr_values_table is not None:
            for row in appr_values_table.xpath("./tr"):
                row = row.xpath("./td/text()").getall()
                if appr_header is None:
                    appr_header = row
                    continue

                if len(row) == 0:
                    continue

                year = row[0]
                try:
                    year = int(year)
                except:
                    continue
                row = dict(zip(appr_header, row))
                appr_rows[year] = row

        logging.debug(appr_rows)

        as_rows = dict()
        as_header = None

        as_values_table = response.xpath('//table[@id="Assessed Values"]')
        if as_values_table is not None:
            for row in as_values_table.xpath("./tr"):
                row = row.xpath("./td/text()").getall()
                if as_header is None:
                    as_header = row
                    continue

                if len(row) == 0:
                    continue

                year = row[0]
                try:
                    year = int(year)
                except:
                    continue
                row = dict(zip(as_header, row))
                as_rows[year] = row

        logging.debug(as_rows)

        meta_dict = {"item": item, "appr_rows": appr_rows, "as_rows": as_rows}

        land_link = response.xpath('//a[./span[text()="Land"]]/@href').get()
        yield response.follow(
            land_link,
            meta=meta_dict,
            callback=self.parse_property_land_page,
            dont_filter=True,
        )

    def parse_property_land_page(self, response):
        item = response.meta.get("item")
        appr_rows = response.meta.get("appr_rows")
        as_rows = response.meta.get("as_rows")

        item["land_area_acres"] = (
            response.xpath('//tr[./td[text()="Acres"]]/td[@class="DataletData"]/text()')
            .get("")
            .replace("\xa0", "")
        )
        if item["land_area_acres"].startswith("."):
            item["land_area_acres"] = 0
        elif item["land_area_acres"] != "":
            item["land_area_acres"] = round(float(item["land_area_acres"]))
        item["land_area_sqft"] = (
            response.xpath(
                '//tr[./td[text()="Square Feet"]]/td[@class="DataletData"]/text()'
            )
            .get("")
            .replace("\xa0", "")
            .replace(",", "")
        )
        item["land_type"] = response.xpath(
            '//tr[./td[text()="Land Type"]]/td[@class="DataletData"]/text()'
        ).get()

        meta_dict = {"item": item, "appr_rows": appr_rows, "as_rows": as_rows}

        sales_link = response.xpath('//a[./span[text()="Sales"]]/@href').get()
        yield response.follow(
            sales_link,
            meta=meta_dict,
            callback=self.parse_property_sales_page,
            dont_filter=True,
        )

    def parse_property_sales_page(self, response):
        item = response.meta.get("item")
        appr_rows = response.meta.get("appr_rows")
        as_rows = response.meta.get("as_rows")

        sale_date_str = response.xpath(
            '//tr[./td[text()="Sale Date"]]/td[@class="DataletData"]/text()'
        ).get()
        if sale_date_str is not None:
            sale_date_str = parse_datetime(sale_date_str).isoformat().replace("T", " ")

        item["sale_datetime"] = sale_date_str
        item["sale_price"] = (
            response.xpath(
                '//tr[./td[text()="Sale Price"]]/td[@class="DataletData"]/text()'
            )
            .get("")
            .replace("$", "")
            .replace(",", "")
        )
        item["seller_1_name"] = (
            response.xpath(
                '//tr[./td[text()="Grantor"]]/td[@class="DataletData"]/text()'
            )
            .get("")
            .replace("\xa0", "")
        )
        item["buyer_1_name"] = (
            response.xpath(
                '//tr[./td[text()="Grantee"]]/td[@class="DataletData"]/text()'
            )
            .get("")
            .replace("\xa0", "")
        )
        item["seller_2_name"] = (
            response.xpath(
                '//tr[./td[text()="Grantor 2"]]/td[@class="DataletData"]/text()'
            )
            .get("")
            .replace("\xa0", "")
        )
        item["buyer_2_name"] = (
            response.xpath(
                '//tr[./td[text()="Grantee 2"]]/td[@class="DataletData"]/text()'
            )
            .get("")
            .replace("\xa0", "")
        )
        item["book"] = response.xpath(
            '//tr[./td[text()="Deed Book"]]/td[@class="DataletData"]/text()'
        ).get()
        item["page"] = response.xpath(
            '//tr[./td[text()="Deed Page"]]/td[@class="DataletData"]/text()'
        ).get()
        item["transfer_deed_type"] = response.xpath(
            '//tr[./td[text()="Instrument Type"]]/td[@class="DataletData"]/text()'
        ).get()
        item[
            "source_url"
        ] = "https://publicaccess.claytoncountyga.gov/search/advancedsearch.aspx?mode=advanced"

        appr_row = appr_rows.get(sale_date.year)
        if appr_row is not None:
            item["total_appraised_value"] = appr_row.get("Total", "").replace(",", "")
            item["land_appraised_value"] = appr_row.get("Land", "").replace(",", "")
            item["building_appraised_value"] = appr_row.get("Building", "").replace(
                ",", ""
            )
        else:
            item["total_appraised_value"] = None
            item["land_appraised_value"] = None
            item["building_appraised_value"] = None

        as_row = as_rows.get(sale_date.year)
        if as_row is not None:
            item["building_assessed_value"] = as_row.get("Buidling", "").replace(
                ",", ""
            )
            item["building_assessed_date"] = sale_date.year
            item["land_assessed_value"] = as_row.get("Land", "").replace(",", "")
            item["total_assessed_value"] = as_row.get("Total", "").replace(",", "")
        else:
            item["building_assessed_value"] = None
            item["building_assessed_value"] = None
            item["land_assessed_value"] = None
            item["total_assessed_value"] = None

        yield item

        next_sale_link = response.xpath(
            '//a[./i[@class="icon-angle-right "]]/@href'
        ).get()
        if next_sale_link is not None:
            yield response.follow(
                next_sale_link,
                callback=self.parse_property_sales_page,
                dont_filter=True,
                meta={"item": item},
            )
            return

        to_from_input_text = response.xpath(
            '//input[@name="DTLNavigator$txtFromTo"]/@value'
        ).get()
        idx, total = to_from_input_text.split(" of ")
        idx = int(idx)
        total = int(total)

        if idx == total:
            yield scrapy.Request(
                self.start_urls[-1],
                callback=self.parse_form_page,
                dont_filter=True,
                meta={"item": item},
            )
            return

        form_data = self.extract_form(response, '//form[@name="frmMain"]')
        del form_data["DTLNavigator$imageNext"]
        del form_data["DTLNavigator$imageLast"]
        form_data["DTLNavigator$imageNext.x"] = "0"  # XXX
        form_data["DTLNavigator$imageNext.y"] = str(idx + 1)
        form_data["hdMode"] = "DEK_PROFILE"
        logging.info(form_data)

        action = response.xpath('//form[@name="frmMain"]/@action').get()
        form_url = urljoin(response.url, action).replace(
            "mode=sales", "mode=dek_profile"
        )

        yield FormRequest(
            form_url,
            formdata=form_data,
            callback=self.parse_property_main_page,
            dont_filter=True,
        )

```

One last thing of interest are the following lines in HTML source code of the site
being scraped:

```html
<meta http-equiv='Description' content='iasWorld'>
<meta name='Copyright' content='Tyler Technologies Inc, Akanda Solutions, LLC'> 
```

This points us to a product names iasWorld by a company called Tyler Technologies, Inc. That
means there's more sites like this and we can reuse the above code to scrape them (some
modifications will be needed).

