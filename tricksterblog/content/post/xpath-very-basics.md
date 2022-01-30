+++
author = "rl1987"
title = "Very basics of XPath: less than 1% of XPath language to scrape more than 90% of pages"
date = "2022-01-31"
draft = true
tags = ["automation", "web-scraping", "python"]
+++

When scraping HTML pages, many developers are using CSS selectors to find the right elements
for data extraction. However, modern HTML is largely based on XML format, which means there
is a better, more powerful way to find the exact elements one needs: XPath. XPath is an entire
language created for traversing XML (and by extension HTML) element trees. The size and complexity
of [XPath 3.1 specification](https://www.w3.org/TR/xpath-31/) might seem daunting, but the good news
is that you need to know very little of it as web scraper developer. 

One way to use XPath in web scraping is to use within Scrapy projects by calling `xpath()` method
on `scrapy.Response` object. Another is to use [lxml](https://lxml.de/) Python module that provides 
a Pythonic API to the funcionality of libxml2 library. Either way, you will get a list of 
result(s) that can be empty if none was found.

Let us go through several examples to demonstrate some key features of XPath that will prove to be 
very useful for web scraping.

Let's start with a very simple example. We want to extract `<h1>` from the following HTML
document:

```html
<html>
  <body>
    <h1>SCRAPE ME</h1>
  </body>
</html>
```

One way to get it is to use XPath like directory/file path: `/html/body/h1`. Another way is to
use two slashes in the beginning of the query to ask for a recursive search within DOM tree:
`//h1`. Yet another way is to go step-by-step across the three levels in the tree: `/html`
gives you the topmost `<html>` element, on which you call `./body` to get the `<body>` 
element in the middle (notice the dot character at the start of query - it denotes that we
want a child element). Lastly, calling `./h1` on the latter gives us the `<h1>` element.

It is very common for HTML elements to have attributes for styling, links and other purposes.
That is very useful when writing XPath queries. As an example, consider the following HTML
document:

```html
<html>
  <body>
    <div id="main">SCRAPE ME</div>
    <div id="secondary">...</div>
  </body>
</html>
```

We want to get the first `<div>` element and don't need the second one. `//div` would return
both of them, but we don't want that. What we do is use brackets and define a predicate:
`//div[@id="main"]`. This specifies that we want to find a `<div>` with `id` exactly matching
value `main`. When specifying a predicate, we can use Boolean operations and write something like:
`//*[@id="main" and not(@id="secondary")]`. This time, we use asterisk character as wildcard to
refrain from specifying exact tag name and forcing the matching exclusively on the predicate.

XPath queries can call functions that XPath language specifies for the use in predicates.
For example, consider the following HTML document:

```html
<html>
  <body>
    <div>ignore</div>
    <div class="a b">ignore</div>
    <div class="a b c">SCRAPE ME</div>
  </body>
</html>
```

We want to get the last `<div>` with `class` attribute having three values. Since this element
is the only having `c` in `class` we can use XPath `contains()` function in the following
query: `//div[contains(@class, "c")]/text()`. Note that we're also calling `text()` at the
end of the query to extract the text from the element. Another way to is to use `contains()`
function to match substring within text of the element we want to match:
`//div[contains(text(), "ME")]/text()`.

We can also use XPath to match an element based on presence of a child element. Consider the 
following HTML

```html
<html>
  <body>
    <div>ignore</div>
    <div>SCRAPE ME<strong>!</strong></div>
  </body>
</html>
```

We specifically want the `<div>` that has `<strong>` child element with a single exclamation mark
in it. The XPath query would be: `//div[./strong[text()="!"]]`.

Lastly, we may want to extract a specific cell from HTML table from document like this:

```html
<html>
  <body>
    <table>
      <tr>
        <th>Data 1</th>
        <th>Data 2</th>
      </tr>
      <tr>
        <td>ignore</td>
        <td>...</td>
      </tr>
      <tr>
        <td>scrape</td>
        <td>SCRAPE ME</td>
      </tr>
    </table>
  </body>
</html>
```

The query to get a `<td>` with `SCRAPE ME` text would be: `//tr[./td[text()="scrape"]]/td[2]`.
This query uses all the XPath feaures we discussed with one more thing: indexing. We say `[2]`
at the end of the query to get the second element from ones it finds. Note that unlike a lot
of programming languages, XPath starts the indices at 1 - beware of off-by-one bugs in your
queries!

The complete example script that demonstrates all these queries is the following - feel free
to modify and play with it:

```python
#!/usr/bin/python3

from lxml import html


def example1():
    print("Example 1")

    html_str = """
<html>
<body>
  <h1>SCRAPE ME</h1>
</body>
</html>
    """

    tree = html.fromstring(html_str)

    h1 = tree.xpath("/html/body/h1")
    print(h1)
    print(h1[0].text)

    h1 = tree.xpath("//h1")
    print(h1)
    print(h1[0].text)
    
    root = tree.xpath('/html')[0]
    body = root.xpath('./body')[0]
    h1 = body.xpath('./h1')
    print(h1)
    print(h1[0].text)


def example2():
    print("Example 2")

    html_str = """
<html>
<body>
  <div id="main">SCRAPE ME</div>
  <div id="secondary">...</div>
</body>
</html>
    """

    tree = html.fromstring(html_str)

    main_div = tree.xpath('//div[@id="main"]')
    print(main_div)
    print(main_div[0].text)

    main_div = tree.xpath('//*[@id="main" and not(@id="secondary")]')
    print(main_div)
    print(main_div[0].text)


def example3():
    print("Example 3")

    html_str = """
<html>
  <body>
    <a href="https://lxml.de" label="SCRAPE ME">lxml</a>
  </body>
</html>
    """

    tree = html.fromstring(html_str)

    label = tree.xpath("//a/@label")
    print(label)


def example4():
    print("Example 4")

    html_str = """
<html>
  <body>
    <div>ignore</div>
    <div class="a b">ignore</div>
    <div class="a b c">SCRAPE ME</div>
  </body>
</html>
    """

    tree = html.fromstring(html_str)

    text = tree.xpath('//div[contains(@class, "c")]/text()')
    print(text)

    text = tree.xpath('//div[contains(text(), "ME")]/text()')
    print(text)


def example5():
    print("Example 5")

    html_str = """
<html>
  <body>
    <div>ignore</div>
    <div>SCRAPE ME<strong>!</strong></div>
  </body>
</html>
    """

    tree = html.fromstring(html_str)

    d = tree.xpath('//div[./strong[text()="!"]]')
    print(d)
    print(d[0].text_content())


def example6():
    print("Example 6")

    html_str = """
<html>
  <body>
    <table>
      <tr>
        <th>Data 1</th>
        <th>Data 2</th>
      </tr>
      <tr>
        <td>ignore</td>
        <td>...</td>
      </tr>
      <tr>
        <td>scrape</td>
        <td>SCRAPE ME</td>
      </tr>
    </table>
  </body>
</html>
    """

    tree = html.fromstring(html_str)

    td = tree.xpath('//tr[./td[text()="scrape"]]/td[2]')
    print(td)
    print(td[0].text)


def main():
    example1()
    example2()
    example3()
    example4()
    example5()
    example6()


if __name__ == "__main__":
    main()
```

You may notice that sometimes `text_content()` is called on the element and sometimes value
is being read from the `text` property. The difference is that calling `text_content()` makes
lxml recursively gather all text from all child elements of given tree, whereas reading
`text` property merely gives you the text that is immediately within the element.

