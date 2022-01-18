+++
author = "rl1987"
title = "Using Python and mitmproxy to scrape private API of mobile app"
date = "2022-01-19"
draft = true
tags = ["python", "mitmproxy", "scraping"]
+++

Web scraping is a widely known way to gather information from external sources. However, it is not the only way. Another way
is API scraping. We define API scraping as activity of automatically extracting data from reverse engineered private APIs.
In this post we will go through an example of reverse engineering private API of a mobile app and developing a simple API
scraping script that reproduces API calls to extract the exact information that app is showing on mobile device.

To exemplify API scraping, we will be extracting a list of ongoing anime TV series form 
[MyAnimeList Official](https://apps.apple.com/us/app/myanimelist-official/id1469330778) app. The part of the app we are
interested in is "This Season" subtab in "Seasonal" tab.

TODO: add screenshot

The tool we will be using for intercepting HTTP traffic is called [mitmproxy](https://mitmproxy.org/). It is a little
HTTP proxy server that can be launched on your computer and provide a way to inspect and modify the HTTP traffic even
if TLS is used. Luckily MAL app does not perform TLS cert pinning which makes it fairly easy to intercept 
private API calls with a proper setup.

In this post, I won't be covering how to set up mitmproxy with your mobile device as there are many blog posts and 
Youtube videos detailing on how to do this with both iOS and Android devices. You may want to check out:

* [Intercept iOS/Android Network Calls using mitmproxy](https://medium.com/testvagrant/intercept-ios-android-network-calls-using-mitmproxy-4d3c94831f62) on Medium
* [Reverse Engineering a Private API with mitmproxy](https://www.youtube.com/watch?v=xQGC-8ojYbU) on Youtube


```python
#!/usr/bin/python3

import csv
from pprint import pprint

import requests

FIELDNAMES = ["title", "synopsis", "status", "genres", "mean"]


def main():
    out_f = open("cur_season.csv", "w", encoding="utf-8")
    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()

    headers = {
        "accept": "*/*",
        "x-mal-client-id": "6591a087c62b3e94d769cd8e35ffe909",
        "cache-control": "public, max-age=60",
        "user-agent": "MAL (ios, 139)",
        "accept-language": "en-GB,en;q=0.9",
    }

    resp1 = requests.get("https://api.myanimelist.net/v3/anime/season", headers=headers)
    print(resp1.url)

    json_dict = resp1.json()

    season = None
    year = None

    for season_dict in json_dict.get("data", []):
        node_dict = season_dict.get("node", dict())
        if node_dict.get("is_current"):
            season = node_dict.get("season")
            year = node_dict.get("year")
            break

    params = {
        "fields": "alternative_titles,media_type,genres,num_episodes,status,start_date,end_date,average_episode_duration,synopsis,mean,rank,popularity,num_list_users,num_favorites,num_scoring_users,start_season,broadcast,my_list_status{start_date,finish_date},favorites_info,nsfw,created_at,updated_at",
        "limit": "50",
        "media_type": "tv",
        "offset": "0",
        "sort": "anime_num_list_users",
        "start_season_season": season,
        "start_season_year": str(year),
    }

    resp2 = requests.get(
        "https://api.myanimelist.net/v3/anime", headers=headers, params=params
    )
    print(resp2.url)

    json_dict = resp2.json()

    for show_dict in json_dict.get("data", []):
        node_dict = show_dict.get("node", dict())

        if node_dict.get("genres") is not None:
            genres = list(map(lambda g: g.get("name"), node_dict.get("genres")))
        else:
            genres = []

        row = {
            "title": node_dict.get("title"),
            "synopsis": node_dict.get("synopsis", "").replace("\n", " "),
            "status": node_dict.get("status"),
            "genres": ",".join(genres),
            "mean": node_dict.get("mean"),
        }

        pprint(row)

        csv_writer.writerow(row)

    out_f.close()


if __name__ == "__main__":
    main()

```
