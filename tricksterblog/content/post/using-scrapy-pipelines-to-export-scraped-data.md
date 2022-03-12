+++
author = "rl1987"
title = "Using Scrapy pipelines to export scraped data"
date = "2022-03-13"
draft = true
tags = ["web-scraping", "python", "scrapy"]
+++

By default Scrapy framework provides a way to export scraped data into CSV, JSON, JSON lines,
XML files with a possibility to store it remotely. However we may need more flexibility in
how and where the scraped data will be stored. This is the purpose of Scrapy item pipelines.
Scrapy pipeline is a component of Scrapy project for implementing post-processing and exporting
of scraped data. We are going to discuss how to implement data export code in pipelines and
provide a couple of examples.

At code level, pipeline is a Python class that implements one or more of the following methods:

* `open_spider()` - called when scraping starts. 
* `process_item()` - called when new item was scraped in the spider.
* `close_spider()` called when scraping ends.
* `from_crawler()` (class method) - factory method that is called from Scrapy crawler object to
create an instance of pipeline class, possibly with some customizations based on project settings.

We will do our preparations to export data in `open_spider()`, process data one item at a time in
`process_item()` and finalise data export in `close_spider()` method.

For the sake of simplicity, we will use [quotesbot](https://github.com/scrapy/quotesbot) Scrapy
project. We will edit pipelines.py file to implement new pipelines and will also make minor changes
to settings.py file to enable newly developed pipelines in the project.

Using openpyxl to write data to Excel file
==========================================

Let us implement `open_spider()` first.

```python
    def open_spider(self, spider):
        self.wb = openpyxl.Workbook()
        self.ws = self.wb.active

        self.ws.append(FIELDNAMES)

```

We instantiated `openpyxl.Workbook` object into instance variable and also saved a reference to
active work sheet (page within spreadsheet). Lastly, we created a header row in the spreadsheet
by appending list of fieldnames. 

Now we can process items. Let us implement `process_item()` method.

```python
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        self.ws.append([adapter.get("text"), adapter.get("author"), ",".join(adapter.get("tags"))])

        return item
```

First, we wrapped the item we have received into `ItemAdapter` object that provides unified API for all kinds
of items we can come across. For such a trivial example this may not be necessary, but it might prove to be useful
in larger, more complex Scrapy project and is generally recommended thing to do. Next, we are calling `append()` on 
openpyxl worksheet object with a list of strings to be appended, ordered in such a way that they line up with
order of fieldnames. This ensures that values of each field are lining up with the header row in the final document.
Note that we cannot write tags directly due to it being a list of strings. To address this issue, we convert it to
a single string by using comma character as separator.

Finally, we need to implement `close_spider()` method where we will call `save()` on openpyxl Workbook to perform
an actual writing to file system.

```python
    def close_spider(self, spider):
        self.wb.save(XLSX_PATH)
```

The entire code for this pipeline is as follows:

```python
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from itemadapter import ItemAdapter

import openpyxl

from quotesbot.settings import XLSX_PATH

FIELDNAMES = ['text', 'author', 'tags']

class XLSXPipeline(object):
    wb = None
    ws = None

    def open_spider(self, spider):
        self.wb = openpyxl.Workbook()
        self.ws = self.wb.active

        self.ws.append(FIELDNAMES)
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        self.ws.append([adapter.get("text"), adapter.get("author"), ",".join(adapter.get("tags"))])

        return item

    def close_spider(self, spider):
        self.wb.save(XLSX_PATH)
```

Now we need to enable this pipeline in settings.py and also set the `XLSX_PATH` configuration setting to some value.
We uncomment `ITEM_PIPELINES` dictionary and edit with a complete class name or our pipeline:

```python
ITEM_PIPELINES = {
    'quotesbot.pipelines.XLSXPipeline': 300,
}
```

We also set the `XLSX_PATH`:

```python
XLSX_PATH = "quotes.xlsx"
```

Running any of the two spiders creates an Excel spreadsheet with scraped data.

TODO: provide screenshot

