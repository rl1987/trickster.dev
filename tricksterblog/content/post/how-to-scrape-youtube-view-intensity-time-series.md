+++
author = "rl1987"
title = "How to scrape Youtube view intensity time series"
date = "2022-03-16"
draft = true
tags = ["web-scraping", "python"]
+++

Recently Youtube has introduced a small graph on it's user interface that visualises a
time series of video viewing intensity. Spikes in this graph indicate what parts of the
video tend to be replayed often, thus being most interesting or relevant to
watch. This requires quite some data to be accumulated and is only available on sufficiently
popular videos.

[Screenshot 1](/2022-06-15_15.11.40.png)

Let us try scraping this data as an exercise in web scraper development. Viewing page source
through the browser and scrolling through it reveals some deep JSON that includes parts
like: 

```json
{"heatMarkerRenderer":{"timeRangeStartMillis":16080,"markerDurationMillis":8040,"heatMarkerIntensityScoreNormalized":0.22363814666380694}}
```

That looks very promising, as this means the time series data is available in the page HTML
and that no further requests are needed to get it. When we scroll higher up, we see that a large
JSON object is being assigned to `ytInitialData` variable. 

[Screenshot 2](/2022-06-15_15.17.54.png)
[Screenshot 3](/2022-06-15_15.23.09.png)

For experimentation, we launch Python REPL and import some usual Python modules that we use
for web scraping and try fetching the page with `requests.get()`.
Since the data is inside JavaScript code, we also import [js2xml](https://github.com/scrapinghub/js2xml)
to parse it.

```
$ python3
Python 3.9.12 (main, Mar 26 2022, 15:51:15)
[Clang 13.1.6 (clang-1316.0.21.2)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import requests
>>> from lxml import html
>>> import js2xml
>>> resp = requests.get("https://www.youtube.com/watch?v=SrsCEbi5N7Y&t=2s")
>>> resp
<Response [200]>
```

So far, so good. We were to get the page HTML without running into any kind of blocking despite
not explicitly setting headers in our request and not managing cookies.

Let's try to extract the JS statement we need.

```
>>> initial_data_js = tree.xpath('//script[starts-with(text(), "var ytInitialData = ")]/text()')
>>> initial_data_js = initial_data_js[0]
>>> initial_data_js[:32]
'var ytInitialData = {"responseCo'
```

Now let us use js2xml to parse it into XML tree.

```
>>> parsed = js2xml.parse(initial_data_js)
>>> parsed
<Element program at 0x10f841e40>
```

Converting deep JSON dictionary into deep XML tree may not seem like much of an improvement. However,
now we can run XPath queries against it. Let us save the XML tree into a file for easier reading.

```
>>> out_f = open("initial_data_js.xml", "w")
>>> out_f.write(js2xml.pretty_print(parsed))
2411766
>>> out_f.close()
```

Now we can open this with a text editor and find the part of tree that contains the data we need:

```xml
                                                <property name="heatMarkers">
                                                  <array>
                                                    <object>
                                                      <property name="heatMarkerRenderer">
                                                        <object>
                                                          <property name="timeRangeStartMillis">
                                                            <number value="0"/>
                                                          </property>
                                                          <property name="markerDurationMillis">
                                                            <number value="8040"/>
                                                          </property>
                                                          <property name="heatMarkerIntensityScoreNormalized">
                                                            <number value="1"/>
                                                          </property>
                                                        </object>
                                                      </property>
                                                    </object>
                                                    <object>
                                                      <property name="heatMarkerRenderer">
                                                        <object>
                                                          <property name="timeRangeStartMillis">
                                                            <number value="8040"/>
                                                          </property>
                                                          <property name="markerDurationMillis">
                                                            <number value="8040"/>
                                                          </property>
                                                          <property name="heatMarkerIntensityScoreNormalized">
                                                            <number value="0.6048726840234977"/>
                                                          </property>
                                                        </object>
                                                      </property>
                                                    </object>

```

Based on this, we can write XPath queries for data extraction:

```
>>> parsed.xpath('//property[@name="heatMarkerRenderer"]')
[<Element property at 0x10f841d80>, <Element property at 0x10f83a3c0>, <Element property at 0x10f83a380>, <Element property at 0x10f83a100>, <Element property at 0x10db1a6c0>, <Element property at 0x10ec91d00>, <Element property at 0x110fd6f40>, <Element property at 0x110fd63c0>, <Element property at 0x110fd6ec0>, <Element property at 0x10ec81f00>, <Element property at 0x110fd6800>, <Element property at 0x110fd6c80>, <Element property at 0x110fd64c0>, <Element property at 0x110fd6dc0>, <Element property at 0x110fd6340>, <Element property at 0x110fd67c0>, <Element property at 0x110fd6440>, <Element property at 0x110fd6400>, <Element property at 0x110fd6fc0>, <Element property at 0x110fd66c0>, <Element property at 0x110fd6500>, <Element property at 0x110fd6cc0>, <Element property at 0x110fd6480>, <Element property at 0x110fd6d40>, <Element property at 0x110fd6380>, <Element property at 0x110fd6b80>, <Element property at 0x110fd6840>, <Element property at 0x110fd6d00>, <Element property at 0x110fd6e00>, <Element property at 0x110fd6740>, <Element property at 0x110fd6880>, <Element property at 0x110fd6c00>, <Element property at 0x110fd6a80>, <Element property at 0x110fd6f80>, <Element property at 0x110fd6540>, <Element property at 0x110fd69c0>, <Element property at 0x110fd6b40>, <Element property at 0x110fd6680>, <Element property at 0x110fd6980>, <Element property at 0x110fd68c0>, <Element property at 0x110fd6e80>, <Element property at 0x110fd6ac0>, <Element property at 0x110fd6b00>, <Element property at 0x110fd6c40>, <Element property at 0x110fd6a40>, <Element property at 0x110fd6a00>, <Element property at 0x110fd6bc0>, <Element property at 0x110fd6580>, <Element property at 0x110fd6780>, <Element property at 0x110fd6e40>, <Element property at 0x110fe0140>, <Element property at 0x110fe0740>, <Element property at 0x110fe09c0>, <Element property at 0x110fe0040>, <Element property at 0x110fe07c0>, <Element property at 0x110fe01c0>, <Element property at 0x110fe0180>, <Element property at 0x110fe0b80>, <Element property at 0x110fe05c0>, <Element property at 0x110fe0d00>, <Element property at 0x110fe0a00>, <Element property at 0x110fe0a80>, <Element property at 0x110fe0fc0>, <Element property at 0x110fe0840>, <Element property at 0x110fe0cc0>, <Element property at 0x110fe0100>, <Element property at 0x110fe0240>, <Element property at 0x110fe0f40>, <Element property at 0x110fe0a40>, <Element property at 0x110fe0600>, <Element property at 0x110fe06c0>, <Element property at 0x110fe0280>, <Element property at 0x110fe0540>, <Element property at 0x110fe0440>, <Element property at 0x110fe08c0>, <Element property at 0x110fe0e00>, <Element property at 0x110fe0ac0>, <Element property at 0x110fe0980>, <Element property at 0x110fe0940>, <Element property at 0x110fe0c80>, <Element property at 0x110fe0b00>, <Element property at 0x110fe0ec0>, <Element property at 0x110fe0c40>, <Element property at 0x110fe0680>, <Element property at 0x110fe0480>, <Element property at 0x110fe0400>, <Element property at 0x110fe0700>, <Element property at 0x110fe0f80>, <Element property at 0x110fe0080>, <Element property at 0x110fe0780>, <Element property at 0x110fe00c0>, <Element property at 0x110fe03c0>, <Element property at 0x110fe0dc0>, <Element property at 0x110fe0580>, <Element property at 0x110fe0880>, <Element property at 0x110fe0900>, <Element property at 0x110fe02c0>, <Element property at 0x110fe0d40>, <Element property at 0x110fe04c0>, <Element property at 0x110fe0200>]
>>> parsed.xpath('//property[@name="heatMarkerRenderer"]')[0].xpath('.//property[@name="timeRangeStartMillis"]/number/@value')
['0']
>>> parsed.xpath('//property[@name="heatMarkerRenderer"]')[-1].xpath('.//property[@name="timeRangeStartMillis"]/number/@value')
['795960']
>>> parsed.xpath('//property[@name="heatMarkerRenderer"]')[-1].xpath('.//property[@name="heatMarkerIntensityScoreNormalized"]/number/@value')
['0.013456379693201089']
>>> parsed.xpath('//property[@name="heatMarkerRenderer"]')[0].xpath('.//property[@name="heatMarkerIntensityScoreNormalized"]/number/@value')
['1']
>>> for hmr in parsed.xpath('//property[@name="heatMarkerRenderer"]'):
...     start = hmr.xpath('.//property[@name="timeRangeStartMillis"]/number/@value')
...     score = hmr.xpath('.//property[@name="heatMarkerIntensityScoreNormalized"]/number/@value')
...     print(start, score)
...
['0'] ['1']
['8040'] ['0.6048726840234977']
['16080'] ['0.22365224428850775']
['24120'] ['0.27094763489610235']
['32160'] ['0.14741887199269307']
['40200'] ['0.076784029975364834']
['48240'] ['0.085744019488653372']
['56280'] ['0.058312826881888297']
['64320'] ['0.036752924777072669']
['72360'] ['0.03365628640622368']
['80400'] ['0.050183479194471192']
['88440'] ['0.057593336089155567']
['96480'] ['0.034168240950240576']
['104520'] ['0.021520086067824129']
['112560'] ['0.0058667693397754829']
['120600'] ['0.023982917121602401']
['128640'] ['0.054083463495605']
['136680'] ['0.11079831293280626']
['144720'] ['0.14804064606274692']
['152760'] ['0.1617291352663259']
['160800'] ['0.22240811982443065']
['168840'] ['0.13413726751153177']
['176880'] ['0.088080834325529697']
['184920'] ['0.057483009795490349']
['192960'] ['0.040814160550204967']
['201000'] ['0.042385478042995778']
['209040'] ['0.067066323491578081']
['217080'] ['0.39149394113095093']
['225120'] ['0.16310203832771014']
['233160'] ['0.21357182135892602']
['241200'] ['0.19529301110503752']
['249240'] ['0.10639527729932123']
['257280'] ['0.28438246206017076']
['265320'] ['0.58298485358007635']
['273360'] ['0.50241718718906136']
['281400'] ['0.29319187203151548']
['289440'] ['0.40353326935938538']
['297480'] ['0.45796861838480818']
['305520'] ['0.30518139791969506']
['313560'] ['0.10516748863879144']
['321600'] ['0.051570373017044355']
['329640'] ['0.037088951461110936']
['337680'] ['0.050998202554842172']
['345720'] ['0.042643104793951211']
['353760'] ['0.025665097485547211']
['361800'] ['0.12987553061675877']
['369840'] ['0.086472314126850164']
['377880'] ['0.1022516073253201']
['385920'] ['0.0093151441911397924']
['393960'] ['0.0046690687650980112']
['402000'] ['0.016322905814324853']
['410040'] ['0.036336073624631912']
['418080'] ['0.095776905627377285']
['426120'] ['0.16380529268309721']
['434160'] ['0.10283409199925106']
['442200'] ['0.077177480387322694']
['450240'] ['0.021710680379162746']
['458280'] ['0.019724091656537029']
['466320'] ['0.036406494451724176']
['474360'] ['0.054331362295421265']
['482400'] ['0.034113380870322924']
['490440'] ['0.020638777415743645']
['498480'] ['0.018437309282101948']
['506520'] ['0.0063348338325342254']
['514560'] ['0.0044191130849080915']
['522600'] ['0']
['530640'] ['0.0099072475133881299']
['538680'] ['0.031019316084096041']
['546720'] ['0.022984068189618654']
['554760'] ['0.017848027959979786']
['562800'] ['0.030471162432826833']
['570840'] ['0.046978193818764453']
['578880'] ['0.097962445358898351']
['586920'] ['0.13967496580138281']
['594960'] ['0.14630756039370915']
['603000'] ['0.10187546650568548']
['611040'] ['0.087378990970205725']
['619080'] ['0.062368607450551332']
['627120'] ['0.024774647142917147']
['635160'] ['0.073689468358129825']
['643200'] ['0.082347861576243478']
['651240'] ['0.019156333053687032']
['659280'] ['0.076731087663138561']
['667320'] ['0.18014944299132968']
['675360'] ['0.19965675734239965']
['683400'] ['0.15902277752560293']
['691440'] ['0.13666601810346865']
['699480'] ['0.042585273664604947']
['707520'] ['0.048912346996792193']
['715560'] ['0.079598398777255164']
['723600'] ['0.090416556134188128']
['731640'] ['0.10795224631259727']
['739680'] ['0.09381178000430275']
['747720'] ['0.066739160272724848']
['755760'] ['0.16440586200572407']
['763800'] ['0.31834117943766299']
['771840'] ['0.2659790863359241']
['779880'] ['0.067401932837569511']
['787920'] ['0.04629072875281575']
['795960'] ['0.013456379693201089']
```

Now let us put all the needed steps into a Python script (and also get the data written
into CSV file):

```python
#!/usr/bin/python3

import csv
import sys

import requests
from lxml import html
import js2xml


def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("{} <youtube_url>".format(sys.argv[0]))
        return

    url = sys.argv[1]

    out_f = open("view_intensity.csv", "w", encoding="utf-8")

    csv_writer = csv.DictWriter(
        out_f, fieldnames=["time", "intensity", "url"], lineterminator="\n"
    )
    csv_writer.writeheader()

    resp = requests.get(url)
    print(resp.url)

    tree = html.fromstring(resp.text)
    initial_data_js = tree.xpath(
        '//script[starts-with(text(), "var ytInitialData = ")]/text()'
    )
    initial_data_js = initial_data_js[0]

    parsed = js2xml.parse(initial_data_js)

    for hmr in parsed.xpath('//property[@name="heatMarkerRenderer"]'):
        start = hmr.xpath('.//property[@name="timeRangeStartMillis"]/number/@value')[0]
        score = hmr.xpath(
            './/property[@name="heatMarkerIntensityScoreNormalized"]/number/@value'
        )[0]
        print(start, score)

        csv_writer.writerow({"time": start, "intensity": score, "url": url})

    out_f.close()


if __name__ == "__main__":
    main()
```

