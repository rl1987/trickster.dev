+++
author = "rl1987"
title = "How to download embedded videos"
date = "2021-11-11"
tags = ["scraping", "youtube", "python"]
+++

When wandering across the World Wide Web, many netizens have come across pages containing Youtube or Vimeo videos embedded in them. [youtube-dl](https://youtube-dl.org/) is a prominent tool to download online videos from many sources (not limited by Youtube - see the [complete list of supported sites](https://ytdl-org.github.io/youtube-dl/supportedsites.html), but can it download the videos even if they are embedded in some third party website? 

Turns out, it can (with a little bit of help from the user). Let me show how.

As our first example, let us [Funnelscripts landing page](https://funnelscripts.com/funnelscripts-webclass). No matter when you open the page, you will see the time ticking down the last few minutes to the presentation. Global market never sleeps. The same applies to Russel Brunson and his elderly friend. No matter the date and time, they are ready to give you a webinar on their SaaS product.

[First image](/2021-11-11_17.31.39.png)

Or do they really? Let's register for the webinar and try to see beyond the facade. Few minutes later, we are able to see what appears to be the stream of the webinar.

[Second image](/2021-11-11_17.43.12.png)

However, opening the Chrome DevTools and exploring DOM a little quickly reveals that iframe with Vimeo player is embedded and playing a prerecorded video.

[Third image](/2021-11-11_17.43.44.png)

Feeding the URL from `src` attribute into youtube-dl lets us download the entire video:

```
$ youtube-dl "https://player.vimeo.com/video/401113675?muted=1&autoplay=1&&title=0&byline=0&wmode=transparent&autopause=0"
[vimeo] 401113675: Downloading webpage
[vimeo] 401113675: Downloading akfire_interconnect_quic m3u8 information
[vimeo] 401113675: Downloading akfire_interconnect_quic m3u8 information
[vimeo] 401113675: Downloading fastly_skyfire m3u8 information
[vimeo] 401113675: Downloading fastly_skyfire m3u8 information
[vimeo] 401113675: Downloading akfire_interconnect_quic MPD information
[vimeo] 401113675: Downloading akfire_interconnect_quic MPD information
[vimeo] 401113675: Downloading fastly_skyfire MPD information
[vimeo] 401113675: Downloading fastly_skyfire MPD information
[hlsnative] Downloading m3u8 manifest
[hlsnative] Total fragments: 1275
[download] Destination: WEBINAR - NO ENCORE-401113675.fhls-fastly_skyfire_sep-2762.mp4
```

However, you may want to download multiple embedded videos. Our second example is [Drop Service Mafia course page](https://dropservicemafia.com/free-course/).
There's multiple Youtube videos we may want downloaded to have something to watch during an inter-continental flight that people will be taking when Bali finally re-opens.

The first video is MP4 file embedded via `<video>` tag and can be downloaded with curl or wget.

[Fourth image](/2021-11-11_18.09.37.png)

Similarly to previous example, we have Youtube videos embedded into HTML code of the page.

[Fifth image](/2021-11-11_18.15.46.png)

We could download these one by one, but let's be smarter about this. Let's write a small Python script that will scrape the Youtube URLs of embedded videos and then let youtube-dl download them.

One thing to note here is that the iframe with Youtube URL at `src` attribute is not present in the HTML code that get downloaded from the server and is created by client-side Javascript. For each video, we get the an element like this:

```
<div class="elementor-element elementor-element-f28e248 elementor-aspect-ratio-169 elementor-widget elementor-widget-video" data-id="f28e248" data-element_type="widget" data-settings="{&quot;youtube_url&quot;:&quot;https:\/\/www.youtube.com\/watch?v=WDBlE0XeGGw&quot;,&quot;video_type&quot;:&quot;youtube&quot;,&quot;controls&quot;:&quot;yes&quot;,&quot;aspect_ratio&quot;:&quot;169&quot;}" data-widget_type="video.default">
```

Note that Youtube URL is present in the JSON string in one of the attribute values.

The code to scrape Youtube URLs and save them into the file is the following.

```python
#!/usr/bin/python3

import json

import requests
from lxml import html


def main():
    resp = requests.get("https://dropservicemafia.com/free-course/")

    tree = html.fromstring(resp.text)

    video_divs = tree.xpath('//div[@data-widget_type="video.default"]')

    out_f = open("urls.txt", "w")

    for video_div in video_divs:
        settings_json = video_div.get("data-settings")
        settings_dict = json.loads(settings_json)

        youtube_url = settings_dict.get("youtube_url")
        if youtube_url is None:
            continue

        out_f.write(youtube_url + "\n")

    out_f.close()


if __name__ == "__main__":
    main()
```

Running this scripts gives urls.txt file containing video links that we can launch youtube-dl with:

```
$ youtube-dl --batch-file=urls.txt
```

