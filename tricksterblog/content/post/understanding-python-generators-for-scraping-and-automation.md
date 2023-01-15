+++
author = "rl1987"
title = "Understanding Python generators for scraping and automation"
date = "2023-01-31"
draft = true
tags = ["python"]
+++

On the [front page of Scrapy framework](https://scrapy.org/) there's the 
following Python snippet:

```python
import scrapy

class BlogSpider(scrapy.Spider):
    name = 'blogspider'
    start_urls = ['https://www.zyte.com/blog/']

    def parse(self, response):
        for title in response.css('.oxy-post-title'):
            yield {'title': title.css('::text').get()}

        for next_page in response.css('a.next'):
            yield response.follow(next_page, self.parse)
```

Note the usage of `yield` keyword in this code. This is different from simply
returning some value from method or function. One way to look at this is that
`yield` is a lazy equivalent of returning a value. All the code that precedes
the `yield` keyword is only executed when the value is needed by the caller.
But there's more to it. To really understand what's going on here, we need
to understand Python generators. To understand Python generators, we need
to understand iterators and to understand iterators we need to understand
iterables.

So, what's an iterable? Iterable is a collection or object that you can
iterate upon in a loop, like this:

```
>>> l = [1, 2, 3]
>>> for x in l:
...     print(x)
... 
1
2
3
```

Common iterables in Python are not just lists, but sequence-like things such 
as sets, tuples, strings:

```
>>> s = set(l)
>>> for x in s:
...     print(x)
... 
1
2
3
>>> t = tuple(l)
>>> for x in t:
...     print(x)
... 
1
2
3
>>> for c in "abcd":
...     print(c)
... 
a
b
c
d
```

When Python runs a for-loop across an iterable, an iterator is implicitly
created and used. Iterator is an object that is similar to database cursor.
It is used to keep track of state (e.g. collection index) across iteration
steps. It is required to implement `__iter()__` method to set the initial state
and `__next__()` method to return the current element from iterable, then update
the state to point to next on. Iterators can also be created explicitly with
an `iter()` function:

```
>>> it = iter(l)
>>> type(it)
<class 'list_iterator'>
```

Using them is simple - just replace an iterable reference with iterator
reference in your for-loop:

```
>>> for x in it:
...     print(x)
... 
1
2
3
```

Once there's nothing else to iterate, the `__next__()` method will raise
a `StopIteration` exception to break the loop.

Sometimes you don't want to use the iterator in for-loop, but just get a single
value from it. This can be done with `next()` function:

```
>>> it = iter("abcd")
>>> print(next(it))
a
>>> print(next(it))
b
```

Now, what's a generator? Generator is a special kind of iterator that does
not go through some iterable, but lazily creates each value when it is needed.
One way a generator can be created is using a generator expression:

```
>>> g = (i*i for i in range(10))
>>> type(g)
<class 'generator'>
>>> next(g)
0
>>> next(g)
1
```

Another way to create a generator is the one typically used in Scrapy projects -
developing a generator function (or method) that uses the `yield` keyword
to lazily return stuff to the caller:

```
>>> def gen_123():
...     print("About to yield 1")
...     yield 1
...     print("About to yield 2")
...     yield 2
...     print("About to yield 3")
...     yield 3
... 
>>> g = gen_123()
>>> type(g)
<class 'generator'>
>>> next(g)
About to yield 1
1
>>> next(g)
About to yield 2
2
>>> next(g)
About to yield 3
3
>>> next(g)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
>>> g = gen_123()
>>> for x in g:
...     print(x)
... 
About to yield 1
1
About to yield 2
2
About to yield 3
3
```

Generator functions/methods can be quite useful in web scraper and bot
development as they enable us to avoid gathering partial or intermediate
results in a collection, which is undesirable from peformance perspective. 
By using generators, we can structure our code as pipeline, with each datum 
going through the processing steps as soon as it is ready. Generator functions
can stateful - all the variables in the function keep their values between the 
moments values are generated.

Consider the following example.

```python
#!/usr/bin/python3

import csv
from urllib.parse import urljoin
from pprint import pprint

import requests
from lxml import html

FIELDNAMES = ["title", "url", "points", "discussion_url"]


def scrape_page(i):
    url = "https://news.ycombinator.com/"
    params = {"p": i}

    resp = requests.get(url, params=params)
    print(resp.url)

    tree = html.fromstring(resp.text)

    for athing_row in tree.xpath('//tr[@class="athing"]'):
        title = athing_row.xpath('.//span[@class="titleline"]/a/text()')[0]
        url = athing_row.xpath('.//span[@class="titleline"]/a/@href')[0]
        points = athing_row.xpath(
            './following-sibling::tr//span[@class="score"]/text()'
        )[0].replace(" points", "")
        discussion_url = athing_row.xpath(
            './following-sibling::tr//span[@class="age"]/a/@href'
        )[0]
        discussion_url = urljoin(resp.url, discussion_url)

        yield {
            "title": title,
            "url": url,
            "points": points,
            "discussion_url": discussion_url,
        }


def scrape(n_pages):
    for i in range(1, n_pages + 1):
        yield from scrape_page(i)


def main():
    out_f = open("hn_posts.csv", "w", encoding="utf-8")

    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()

    for row in scrape(3):
        pprint(row)
        csv_writer.writerow(row)

    out_f.close()


if __name__ == "__main__":
    main()
```

Here we scrape the first three pages of Hacker News. For each posted link 
we get an URL, title, number of points and link to discussion page. All of that
is being written to CSV file - one row at a time. Using generator functions we
can refrain from wasting resources putting each row into a list or set and
then iterating across that collection when writing it out into a file. 
Furthermore, this is more desirable from error handling perspective, as we would
not lose all the data if the script crashed (error handling has been omitted for
the sake of brevity). 

Both `scrape_page()` and `scrape()` are generator functions. `scrape_page()`
scrapes an `i`-th page from Hacker News and generates item dictionaries one at
a time. If we just wanted a single page worth of data, we could just iterate
over it on the caller side and get each row when it was generated. However
we have `scrape()` function in the middle that demonstrates iterator chaining
with a fairly new Python feature - `yield from`. In this case, `yield from`
is only used to avoid doing it like this:

```python
for i in range(1, n_pages + 1)):
    for row in scrape_page(i):
        yield row
```

More generally, `yield from` establishes a connection between caller and 
sub-generator.

In Scrapy framework generators are used in conjunction with asynchronuous
networking. Your Scrapy spider callbacks contain code that is lazily evaluated
exactly when needed and use `yield` keyword to generate a request or data
item both when it is ready and when the underlying machinery of Scrapy is able
to process it.

