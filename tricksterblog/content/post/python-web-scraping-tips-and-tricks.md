+++
author = "rl1987"
title = "Python Web Scraping: tips and tricks"
date = "2022-01-05"
draft = true
tags = ["python", "web-scraping"]
+++

Use pandas `read_html()` to parse HTML tables (when possible)
-----------------------------------------------------------

Some pages you might be scraping might include old-school HTML `<table>` elements with tabular data.
There's an easy way to extract data from pages like this with into Pandas dataframes (although you may need to
clean up it afterward):

```python
>>> import pandas as pd
>>> pd.read_html('https://en.wikipedia.org/wiki/Yakutsk')[0]
                                      Yakutsk  Якутск                                  Yakutsk  Якутск.1
0                 City under republic jurisdiction[1]                City under republic jurisdiction[1]
1                              Other transcription(s)                             Other transcription(s)
2                                             • Yakut                                         Дьокуускай
3                        Central Yakutsk from the air                       Central Yakutsk from the air
4   .mw-parser-output .ib-settlement-cols{text-ali...  .mw-parser-output .ib-settlement-cols{text-ali...
5                                 Location of Yakutsk                                Location of Yakutsk
6   .mw-parser-output .locmap .od{position:absolut...  .mw-parser-output .locmap .od{position:absolut...
7   Coordinates: .mw-parser-output .geo-default,.m...  Coordinates: .mw-parser-output .geo-default,.m...
8                                             Country                                             Russia
9                                     Federal subject                                  Sakha Republic[2]
10                                            Founded                                               1632
11                                  City status since                                               1643
12                                         Government                                         Government
13                                             • Body                                      Okrug Council
14                                             • Head                                   Evgeny Grigoriev
15                                               Area                                               Area
16                                            • Total                                 122 km2 (47 sq mi)
17                                          Elevation                                      95 m (312 ft)
18                                         Population                                         Population
19                               • Estimate (2018)[3]                                             311760
20                                             • Rank                                       68th in 2010
21                              Administrative status                              Administrative status
22                                  • Subordinated to        city of republic significance of Yakutsk[1]
23                                       • Capital of                                  Sakha Republic[2]
24                                       • Capital of        city of republic significance of Yakutsk[1]
25                                   Municipal status                                   Municipal status
26                                      • Urban okrug                             Yakutsk Urban Okrug[4]
27                                       • Capital of                             Yakutsk Urban Okrug[4]
28                                          Time zone                                  UTC+9 (MSK+6 [5])
29                                  Postal code(s)[6]                                             677xxx
30                                    Dialing code(s)                                         +7 4112[7]
31                                           OKTMO ID                                        98701000001
32                                           City Day                         Second Sunday of September
33                                            Website                                          якутск.рф
```

Look for JSON snippets inside HTML and extract them
---------------------------------------------------

Some sites have pages with JSON snippets that are meant to be parsed by search engines. They provide pre-structured data
and can save you some hassle with trying to get your XPath queries or CSS selectors right.

See schema.org specification for examples of what you might find on sites that want to make search engine crawling easier.

Use js2xml to extract data from JavaScript snippets
---------------------------------------------------

On the other hand, some sites will give you pages with JavaScript snippets containing data you want to scrape.
It is a bit of a hassle to use regular expressions or basic string processing techniques to extract the data.
Luckily, there is a Python module called [js2xml](https://github.com/scrapinghub/js2xml) developed by Zyte, the
creators of Scrapy framework. This module converts JS code into XML trees that you can run XPath queries against.

The official README file provides the following example:

```python
>>> import js2xml
>>>
>>> jscode = """function factorial(n) {
...     if (n === 0) {
...         return 1;
...     }
...     return n * factorial(n - 1);
... }"""
>>> parsed = js2xml.parse(jscode)
>>>
>>> parsed.xpath("//funcdecl/@name")  # extracts function name
['factorial']
>>>
>>> print(js2xml.pretty_print(parsed))  # pretty-print generated XML
<program>
  <funcdecl name="factorial">
    <parameters>
      <identifier name="n"/>
    </parameters>
    <body>
      <if>
        <predicate>
          <binaryoperation operation="===">
            <left>
              <identifier name="n"/>
            </left>
            <right>
              <number value="0"/>
            </right>
          </binaryoperation>
        </predicate>
        <then>
          <block>
            <return>
              <number value="1"/>
            </return>
          </block>
        </then>
      </if>
      <return>
        <binaryoperation operation="*">
          <left>
            <identifier name="n"/>
          </left>
          <right>
            <functioncall>
              <function>
                <identifier name="factorial"/>
              </function>
              <arguments>
                <binaryoperation operation="-">
                  <left>
                    <identifier name="n"/>
                  </left>
                  <right>
                    <number value="1"/>
                  </right>
                </binaryoperation>
              </arguments>
            </functioncall>
          </right>
        </binaryoperation>
      </return>
    </body>
  </funcdecl>
</program>

>>>
```

Launch `lynx --dump` to quickly extract text
--------------------------------------------

[Lynx](https://lynx.invisible-island.net/) is text-only web browser dating back to the early days of World Wide Web. It has a CLI option
to quickly extract text from simple web pages:

```
$ lynx --dump https://quotes.toscrape.com/
[1]Quotes to Scrape

   [2]Login
   "The world as we have created it is a process of our thinking. It
   cannot be changed without changing our thinking." by Albert Einstein
   [3](about)
   Tags:
   [4]change [5]deep-thoughts [6]thinking [7]world
   "It is our choices, Harry, that show what we truly are, far more than
   our abilities." by J.K. Rowling [8](about)
   Tags:
   [9]abilities [10]choices
   "There are only two ways to live your life. One is as though nothing is
   a miracle. The other is as though everything is a miracle." by Albert
   Einstein [11](about)
   Tags:
   [12]inspirational [13]life [14]live [15]miracle [16]miracles

   "The person, be it gentleman or lady, who has not pleasure in a good
   novel, must be intolerably stupid." by Jane Austen [17](about)
   Tags:
   [18]aliteracy [19]books [20]classic [21]humor

   "Imperfection is beauty, madness is genius and it's better to be
   absolutely ridiculous than absolutely boring." by Marilyn Monroe
   [22](about)
   Tags:
   [23]be-yourself [24]inspirational

   "Try not to become a man of success. Rather become a man of value." by
   Albert Einstein [25](about)
   Tags:
   [26]adulthood [27]success [28]value

   "It is better to be hated for what you are than to be loved for what
   you are not." by Andr? Gide [29](about)
   Tags:
   [30]life [31]love

   "I have not failed. I've just found 10,000 ways that won't work." by
   Thomas A. Edison [32](about)
   Tags:
   [33]edison [34]failure [35]inspirational [36]paraphrased

   "A woman is like a tea bag; you never know how strong it is until it's
   in hot water." by Eleanor Roosevelt [37](about)
   Tags:
   [38]misattributed-eleanor-roosevelt

   "A day without sunshine is like, you know, night." by Steve Martin
   [39](about)
   Tags:
   [40]humor [41]obvious [42]simile

     * [43]Next ->

Top Ten tags

   [44]love [45]inspirational [46]life [47]humor [48]books [49]reading
   [50]friendship [51]friends [52]truth [53]simile

   Quotes by: [54]GoodReads.com

   Made with ? by [55]Scrapinghub

References

   1. https://quotes.toscrape.com/
   2. https://quotes.toscrape.com/login
   3. https://quotes.toscrape.com/author/Albert-Einstein
   4. https://quotes.toscrape.com/tag/change/page/1/
   5. https://quotes.toscrape.com/tag/deep-thoughts/page/1/
   6. https://quotes.toscrape.com/tag/thinking/page/1/
   7. https://quotes.toscrape.com/tag/world/page/1/
   8. https://quotes.toscrape.com/author/J-K-Rowling
   9. https://quotes.toscrape.com/tag/abilities/page/1/
  10. https://quotes.toscrape.com/tag/choices/page/1/
  11. https://quotes.toscrape.com/author/Albert-Einstein
  12. https://quotes.toscrape.com/tag/inspirational/page/1/
  13. https://quotes.toscrape.com/tag/life/page/1/
  14. https://quotes.toscrape.com/tag/live/page/1/
  15. https://quotes.toscrape.com/tag/miracle/page/1/
  16. https://quotes.toscrape.com/tag/miracles/page/1/
  17. https://quotes.toscrape.com/author/Jane-Austen
  18. https://quotes.toscrape.com/tag/aliteracy/page/1/
  19. https://quotes.toscrape.com/tag/books/page/1/
  20. https://quotes.toscrape.com/tag/classic/page/1/
  21. https://quotes.toscrape.com/tag/humor/page/1/
  22. https://quotes.toscrape.com/author/Marilyn-Monroe
  23. https://quotes.toscrape.com/tag/be-yourself/page/1/
  24. https://quotes.toscrape.com/tag/inspirational/page/1/
  25. https://quotes.toscrape.com/author/Albert-Einstein
  26. https://quotes.toscrape.com/tag/adulthood/page/1/
  27. https://quotes.toscrape.com/tag/success/page/1/
  28. https://quotes.toscrape.com/tag/value/page/1/
  29. https://quotes.toscrape.com/author/Andre-Gide
  30. https://quotes.toscrape.com/tag/life/page/1/
  31. https://quotes.toscrape.com/tag/love/page/1/
  32. https://quotes.toscrape.com/author/Thomas-A-Edison
  33. https://quotes.toscrape.com/tag/edison/page/1/
  34. https://quotes.toscrape.com/tag/failure/page/1/
  35. https://quotes.toscrape.com/tag/inspirational/page/1/
  36. https://quotes.toscrape.com/tag/paraphrased/page/1/
  37. https://quotes.toscrape.com/author/Eleanor-Roosevelt
  38. https://quotes.toscrape.com/tag/misattributed-eleanor-roosevelt/page/1/
  39. https://quotes.toscrape.com/author/Steve-Martin
  40. https://quotes.toscrape.com/tag/humor/page/1/
  41. https://quotes.toscrape.com/tag/obvious/page/1/
  42. https://quotes.toscrape.com/tag/simile/page/1/
  43. https://quotes.toscrape.com/page/2/
  44. https://quotes.toscrape.com/tag/love/
  45. https://quotes.toscrape.com/tag/inspirational/
  46. https://quotes.toscrape.com/tag/life/
  47. https://quotes.toscrape.com/tag/humor/
  48. https://quotes.toscrape.com/tag/books/
  49. https://quotes.toscrape.com/tag/reading/
  50. https://quotes.toscrape.com/tag/friendship/
  51. https://quotes.toscrape.com/tag/friends/
  52. https://quotes.toscrape.com/tag/truth/
  53. https://quotes.toscrape.com/tag/simile/
  54. https://www.goodreads.com/quotes
  55. https://scrapinghub.com/
```

If you are doing some Natural Language Processing and do not want to spend too much time on web scraping it might
be a helpful shortcut to call a command like this through Python `subprocess` module.

Use `multiprocessing.dummy` for easy multithreading of highly parallel tasks
----------------------------------------------------------------------------

For spreading the workload across a pool of child worker processes, Python provides us with `multiprocessing`
module. However, web scraping scripts are typically I/O bound and not CPU bound. It makes more sense to
distribute workload across threads, not processes. Luckily, Python developers were kind enough to provide us
with [`multiprocessing.dummy`](https://docs.python.org/3/library/multiprocessing.html#module-multiprocessing.dummy)
module that has the same API as `multiprocessing`, but will create and use a pool of worker threads instead.
For example, one could initialize a thread pool object and call the `map()` method with two arguments: 1) function
to scrape single page and 2) list of page URLs. The thread pool will automatically run the requests concurrently and
return a list of results. You may not want to wait for all results to come at once and may prefer to incrementally receive
them as they become ready. This can be achieved with `imap()` method of `ThreadPool`.

