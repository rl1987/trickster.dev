+++
author = "rl1987"
title = "Retrospective scraping of historical data from Internet Archive snapshots"
date = "2023-12-27"
draft = true
tags = ["scraping", "osint", "python"]
+++

Some internet research activities are based not only on the present data, but also
on historical data that was, but no longer is posted online. As of late 2023, 
Internet Archive has over 842 billion web page snapshots stored and available 
for retrieval.  We will go through a simple example of how scraping pre-crawled 
pages from Wayback Machine can be used to gather historical data for data science 
purposes. To look into Iowa inmate population trends, we will be scraping historical 
snapshots of Iowa Department of Corrections [inmate statistics page](https://doc-search.iowa.gov/dailystatistics). 
Data of interest is in "Current Count" and "Institution" columns of the table. 
For scraping we will use Python with requests and lxml modules. For dataviz we 
will use Jupyter, Pandas and Matplotlib.

To quickly view the available snapshots for this page we search it through 
[Archive.org front page](https://archive.org). But there seems to be a little
complication. Only two snapshots are available, which would not be sufficient 
for our purposes.

Thus we must backtrack a little. Searching for the domain - `doc-search.iowa.gov` -
on Wayback Machine gives us only 5 snapshots. It seems this domain is pointing
to fairly new (sub)site that is primarily meant for looking up prisoners in
Iowa and only secondarily to provide overall inmate statistics. The primary
domain for Iowa Dept. of Corrections is doc.iowa.gov. Exploring snapshots
for this site reveals that until some time in 2023 it had a statistics page
at following URL:

* https://doc.iowa.gov/daily-statistics

We are after data on all available snapshots of this page.

To check for snapshot availability we can call the 
[`/wayback/available`](https://archive.org/developers/_static/test-wayback.html)
API endpoint with the URL of interest:

```
$ curl "https://archive.org/wayback/available?url=https://doc.iowa.gov/daily-statistics" | jq
{
  "url": "https://doc.iowa.gov/daily-statistics",
  "archived_snapshots": {
    "closest": {
      "status": "200",
      "available": true,
      "url": "http://web.archive.org/web/20230429064712/https://doc.iowa.gov/daily-statistics",
      "timestamp": "20230429064712"
    }
  }
}
```

How do we get the list of snapshots? Internet Archive 
[CDX API](https://archive.org/developers/wayback-cdx-server.html) is a flexible
way to search for snapshots by URL and secondary criteria: HTTP status code,
timeframe and MIME type of the content. By default this API provides output
in CDX table format that looks as follows:

```
$ curl "http://web.archive.org/cdx/search/cdx?url=doc.iowa.gov&limit=5"
gov,iowa,doc)/ 20170323172420 https://doc.iowa.gov/ text/html 200 L4NPH6MSVTZBRCD6CUTTQ2Y66OKY5Y3S 6904
gov,iowa,doc)/ 20170323172435 https://doc.iowa.gov/ text/html 200 BPFQVM2VIW32BNVM7LJ23QTXN7TDTPIL 6906
gov,iowa,doc)/ 20170323172720 https://doc.iowa.gov/ text/html 200 76LUVXUPNL3NPGU246YM3YQ6VNOOVIVH 6907
gov,iowa,doc)/ 20170416221430 https://doc.iowa.gov/ text/html 200 6VMMWJRPN33DAGREX54WSLFG367NCCEF 7113
gov,iowa,doc)/ 20170417071150 https://doc.iowa.gov/ text/html 200 OZMIM56F6OM5IL3HXTWBJZQCMGVRBYTB 7119
```

We can get a JSONified version of this table by passing `output=json` URL parameter:

```
$ curl "http://web.archive.org/cdx/search/cdx?url=doc.iowa.gov&limit=5&output=json"
[["urlkey","timestamp","original","mimetype","statuscode","digest","length"],
["gov,iowa,doc)/", "20170323172420", "https://doc.iowa.gov/", "text/html", "200", "L4NPH6MSVTZBRCD6CUTTQ2Y66OKY5Y3S", "6904"],
["gov,iowa,doc)/", "20170323172435", "https://doc.iowa.gov/", "text/html", "200", "BPFQVM2VIW32BNVM7LJ23QTXN7TDTPIL", "6906"],
["gov,iowa,doc)/", "20170323172720", "https://doc.iowa.gov/", "text/html", "200", "76LUVXUPNL3NPGU246YM3YQ6VNOOVIVH", "6907"],
["gov,iowa,doc)/", "20170416221430", "https://doc.iowa.gov/", "text/html", "200", "6VMMWJRPN33DAGREX54WSLFG367NCCEF", "7113"],
["gov,iowa,doc)/", "20170417071150", "https://doc.iowa.gov/", "text/html", "200", "OZMIM56F6OM5IL3HXTWBJZQCMGVRBYTB", "7119"]]
```

This is still not quite the shape of data that most modern JSON APIs provide, 
but we can work with that by using [`read_json()` function](https://pandas.pydata.org/docs/reference/api/pandas.read_json.html)
from Pandas:

```
$ python3
Python 3.11.6 (main, Oct  2 2023, 20:46:14) [Clang 14.0.3 (clang-1403.0.22.14.1)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import pandas as pd
>>> df = pd.read_json("http://web.archive.org/cdx/search/cdx?url=doc.iowa.gov&limit=5&output=json")
>>> df
                0               1                      2          3           4                                 5       6
0          urlkey       timestamp               original   mimetype  statuscode                            digest  length
1  gov,iowa,doc)/  20170323172420  https://doc.iowa.gov/  text/html         200  L4NPH6MSVTZBRCD6CUTTQ2Y66OKY5Y3S    6904
2  gov,iowa,doc)/  20170323172435  https://doc.iowa.gov/  text/html         200  BPFQVM2VIW32BNVM7LJ23QTXN7TDTPIL    6906
3  gov,iowa,doc)/  20170323172720  https://doc.iowa.gov/  text/html         200  76LUVXUPNL3NPGU246YM3YQ6VNOOVIVH    6907
4  gov,iowa,doc)/  20170416221430  https://doc.iowa.gov/  text/html         200  6VMMWJRPN33DAGREX54WSLFG367NCCEF    7113
5  gov,iowa,doc)/  20170417071150  https://doc.iowa.gov/  text/html         200  OZMIM56F6OM5IL3HXTWBJZQCMGVRBYTB    7119
```

It misread column labels in the first line, but we can trivially fix it:

```
>>> headers = df.iloc[0]
>>> df = pd.DataFrame(df.values[1:], columns=headers)
>>> df
0          urlkey       timestamp               original   mimetype statuscode                            digest length
0  gov,iowa,doc)/  20170323172420  https://doc.iowa.gov/  text/html        200  L4NPH6MSVTZBRCD6CUTTQ2Y66OKY5Y3S   6904
1  gov,iowa,doc)/  20170323172435  https://doc.iowa.gov/  text/html        200  BPFQVM2VIW32BNVM7LJ23QTXN7TDTPIL   6906
2  gov,iowa,doc)/  20170323172720  https://doc.iowa.gov/  text/html        200  76LUVXUPNL3NPGU246YM3YQ6VNOOVIVH   6907
3  gov,iowa,doc)/  20170416221430  https://doc.iowa.gov/  text/html        200  6VMMWJRPN33DAGREX54WSLFG367NCCEF   7113
4  gov,iowa,doc)/  20170417071150  https://doc.iowa.gov/  text/html        200  OZMIM56F6OM5IL3HXTWBJZQCMGVRBYTB   7119
```

From the timestamp column we can derive the snapshot URL by treating the timestamp
as path component between `https://web.archive.org/web/` and the original URL:

```
>>> df['snapshot_url'] = df['timestamp'].apply(lambda ts: 'https://web.archive.org/web/' + ts + '/https://doc.iowa.gov/')
>>> df['snapshot_url'].to_list()
['https://web.archive.org/web/20170323172420/https://doc.iowa.gov/', 'https://web.archive.org/web/20170323172435/https://doc.iowa.gov/', 'https://web.archive.org/web/20170323172720/https://doc.iowa.gov/', 'https://web.archive.org/web/20170416221430/https://doc.iowa.gov/', 'https://web.archive.org/web/20170417071150/https://doc.iowa.gov/']
```

Each snapshot is the original HTML page with some extra stuff injected to help
us navigate the history of the page. Thus we can scrape it by using all the
usual web scraping techniques.

Some open source projects relying on Internet Archive API:

* [gau](https://github.com/lc/gau) - a recon tool to fetch known URLs from several
sources, including Internet Archive.
* Bellingcat's [wayback-google-analytics](https://github.com/bellingcat/wayback-google-analytics)
is OSINT tool to dig up Google Analytics identifiers for finding associations
between websites.

