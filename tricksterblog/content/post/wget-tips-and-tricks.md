+++
author = "rl1987"
title = "Wget tips and tricks"
date = "2022-11-11"
draft = true
tags = ["scraping", "automation"]
+++

So, what is wget? [Wget](https://www.gnu.org/software/wget/) is a prominent command
line tool to download stuff from the web. It has a fairly extensive feature set that
includes recursive downloading, proxy support, site mirroring, cookie handling and so
on. Let us  go through some use cases of wget. 

To download a single file/page using wget, just pass the corresponding URL into `argv[1]`:

```
$ wget http://www.textfiles.com/100/crossbow
--2022-11-11 18:24:33--  http://www.textfiles.com/100/crossbow
Resolving www.textfiles.com (www.textfiles.com)... 208.86.224.90
Connecting to www.textfiles.com (www.textfiles.com)|208.86.224.90|:80... connected.
HTTP request sent, awaiting response... 200 OK
Length: 29200 (29K)
Saving to: ‘crossbow’

crossbow                                           100%[================================================================================================================>]  28,52K   114KB/s    in 0,3s    

2022-11-11 18:24:33 (114 KB/s) - ‘crossbow’ saved [29200/29200]

```

This shows us the HTTP status code, server IP address, file size and even visualises
the progress on ASCII-art progress bar. This is default level of output verbosity. 
But what if we wanted to see more details? Perhaps something is off and we want to 
troubleshoot it? We can enable debug output by using `--debug`:

```
$ wget --debug http://www.textfiles.com/100/crossbow
DEBUG output created by Wget 1.21.3 on darwin21.3.0.

Reading HSTS entries from /Users/rl/.wget-hsts
URI encoding = ‘UTF-8’
Converted file name 'crossbow' (UTF-8) -> 'crossbow' (UTF-8)
--2022-11-11 18:26:48--  http://www.textfiles.com/100/crossbow
Resolving www.textfiles.com (www.textfiles.com)... 208.86.224.90
Caching www.textfiles.com => 208.86.224.90
Connecting to www.textfiles.com (www.textfiles.com)|208.86.224.90|:80... connected.
Created socket 5.
Releasing 0x0000600000a3aae0 (new refcount 1).

---request begin---
GET /100/crossbow HTTP/1.1
Host: www.textfiles.com
User-Agent: Wget/1.21.3
Accept: */*
Accept-Encoding: identity
Connection: Keep-Alive

---request end---
HTTP request sent, awaiting response... 
---response begin---
HTTP/1.1 200 OK
Date: Fri, 11 Nov 2022 10:26:49 GMT
Server: Apache/2.4.54 (FreeBSD) OpenSSL/1.1.1o-freebsd
Last-Modified: Sun, 01 Aug 1999 17:20:50 GMT
ETag: "7210-35109efcee080"
Accept-Ranges: bytes
Content-Length: 29200
Keep-Alive: timeout=5, max=100
Connection: Keep-Alive

---response end---
200 OK
Registered socket 5 for persistent reuse.
Length: 29200 (29K)
Saving to: ‘crossbow.1’

crossbow.1                                         100%[================================================================================================================>]  28,52K   112KB/s    in 0,3s    

2022-11-11 18:26:49 (112 KB/s) - ‘crossbow.1’ saved [29200/29200]

```

We got the HTTP message headers and even some socket lifecycle logs.

If we wanted to make output less verbose than it usually is, we could use
`--no-verbose`:

```
$ wget --no-verbose http://www.textfiles.com/100/crossbow
2022-11-11 18:30:32 URL:http://www.textfiles.com/100/crossbow [29200/29200] -> "crossbow.2" [1]
```

To make the wget print no output, run it with `--quiet`.

If you want to download something from legacy FTP server you can do it with wget. Running
wget with directory URL fetches the file list for that directory and converts it to HTML
(don't forget slash character at the end):

```
$ wget ftp://ftp.cs.brown.edu/pub/
--2022-11-11 18:37:22--  ftp://ftp.cs.brown.edu/pub/
           => ‘.listing’
Resolving ftp.cs.brown.edu (ftp.cs.brown.edu)... 128.148.32.111
Connecting to ftp.cs.brown.edu (ftp.cs.brown.edu)|128.148.32.111|:21... connected.
Logging in as anonymous ... Logged in!
==> SYST ... done.    ==> PWD ... done.
==> TYPE I ... done.  ==> CWD (1) /pub ... done.
==> PASV ... done.    ==> LIST ... done.

.listing                                               [ <=>                                                                                                             ]   6,16K  --.-KB/s    in 0s      

2022-11-11 18:37:24 (55,2 MB/s) - ‘.listing’ saved [6312]

Removed ‘.listing’.
Wrote HTML-ized index to ‘index.html’ [9267].
```

Once we have chosen a file to download, we can do it the same way as with HTTP protocol:

```
$ wget ftp://ftp.cs.brown.edu/pub/README 
--2022-11-11 18:39:53--  ftp://ftp.cs.brown.edu/pub/README
           => ‘README’
Resolving ftp.cs.brown.edu (ftp.cs.brown.edu)... 128.148.32.111
Connecting to ftp.cs.brown.edu (ftp.cs.brown.edu)|128.148.32.111|:21... connected.
Logging in as anonymous ... Logged in!
==> SYST ... done.    ==> PWD ... done.
==> TYPE I ... done.  ==> CWD (1) /pub ... done.
==> SIZE README ... 7998
==> PASV ... done.    ==> RETR README ... done.
Length: 7998 (7,8K) (unauthoritative)

README                                             100%[================================================================================================================>]   7,81K  --.-KB/s    in 0,006s  

2022-11-11 18:39:56 (1,25 MB/s) - ‘README’ saved [7998]


```

Now, what if we wanted wget to follow links and traverse pages recursively to download
entire website? This is called website mirroring and wget has multiple CLI options
to support this use case:

* `--adjust-extension` fixes the extension of downloaded HTML pages.
* `--recursive`, `-r` enables recursive crawling (default depth is 5).
* `--level`, `-l` specifies crawl depth.
* `--convert-links`, `-k` converts links in HTML pages so that they are suitable for local viewing.
* `--domains`, `-D` specifies a comma-separated list of domains to set boundaries when crawling.
* `--mirror` enables mirroring mode.

For example, we could run:

```
$ wget --mirror --domains quotes.toscrape.com,fonts.googleapis.com,fonts.gstatic.com --convert-links  https://quotes.toscrape.com
```

This would download a static website for offline browsing.

Now, what do we do if there's a login wall or something similar standing in our way? We may need
to submit a login form or press a button to get a cookie that would allow us to download a file.
Fortunately, we can use wget with `--post-data` to submit form data and `--save-cookies` to save 
cookies into file. We also need to use `--keep-session-cookies` so that cookies without 
expiration date would be saved as well.

The command to reproduce VMWare Customer Connect login action would be the following:

```
$ wget --keep-session-cookies --save-cookies cookies.txt --post-data "username=[REDACTED]&password=[REDACTED]" "https://auth.vmware.com/oam/server/auth_cred_submit?Auth-AppID=WMVMWR"
```

Now we have some cookies saved into text file. We can use them with `--load-cookies` to 
download some software we have from VMWare:

```
$ wget --load-cookies cookies.txt https://download3.vmware.com/software/FUS-1224/VMware-Fusion-12.2.4-20071091_x86.dmg
```

The last use case we want to look into is user wget as a crawler that saves a list of pages it
goes through as it traverses the site. To this purpose we can use `--spider` and `--delete-after`
with some of the CLI options we utilised when we did the mirroring:

```
$ wget --no-verbose --recursive --domains quotes.toscrape.com,fonts.googleapis.com,fonts.gstatic.com --spider --delete-after https://quotes.toscrape.com 2>&1 | tee wget_urls.txt 
2022-11-11 20:25:07 URL:https://quotes.toscrape.com/ [11053/11053] -> "quotes.toscrape.com/index.html.tmp.tmp" [1]
https://quotes.toscrape.com/robots.txt:
2022-11-11 20:25:07 ERROR 404: NOT FOUND.
2022-11-11 20:25:10 URL:https://quotes.toscrape.com/static/bootstrap.min.css [125934/125934] -> "quotes.toscrape.com/static/bootstrap.min.css.tmp.tmp" [1]
2022-11-11 20:25:11 URL:https://quotes.toscrape.com/static/main.css [1370/1370] -> "quotes.toscrape.com/static/main.css.tmp.tmp" [1]
2022-11-11 20:25:11 URL:https://quotes.toscrape.com/login [1869/1869] -> "quotes.toscrape.com/login.tmp.tmp" [1]
2022-11-11 20:25:12 URL:http://quotes.toscrape.com/author/Albert-Einstein/ [5324/5324] -> "quotes.toscrape.com/author/Albert-Einstein.tmp.tmp" [1]
http://quotes.toscrape.com/robots.txt:
2022-11-11 20:25:13 ERROR 404: NOT FOUND.
2022-11-11 20:25:14 URL:https://quotes.toscrape.com/tag/change/page/1/ [3851/3851] -> "quotes.toscrape.com/tag/change/page/1/index.html.tmp.tmp" [1]
2022-11-11 20:25:15 URL:https://quotes.toscrape.com/tag/deep-thoughts/page/1/ [3865/3865] -> "quotes.toscrape.com/tag/deep-thoughts/page/1/index.html.tmp.tmp" [1]
2022-11-11 20:25:16 URL:https://quotes.toscrape.com/tag/thinking/page/1/ [4687/4687] -> "quotes.toscrape.com/tag/thinking/page/1/index.html.tmp.tmp" [1]
2022-11-11 20:25:16 URL:https://quotes.toscrape.com/tag/world/page/1/ [3849/3849] -> "quotes.toscrape.com/tag/world/page/1/index.html.tmp.tmp" [1]
2022-11-11 20:25:18 URL:http://quotes.toscrape.com/author/J-K-Rowling/ [5343/5343] -> "quotes.toscrape.com/author/J-K-Rowling.tmp.tmp" [1]
2022-11-11 20:25:19 URL:https://quotes.toscrape.com/tag/abilities/page/1/ [3638/3638] -> "quotes.toscrape.com/tag/abilities/page/1/index.html.tmp.tmp" [1]
2022-11-11 20:25:19 URL:https://quotes.toscrape.com/tag/choices/page/1/ [3634/3634] -> "quotes.toscrape.com/tag/choices/page/1/index.html.tmp.tmp" [1]
2022-11-11 20:25:21 URL:https://quotes.toscrape.com/tag/inspirational/page/1/ [12815/12815] -> "quotes.toscrape.com/tag/inspirational/page/1/index.html.tmp.tmp" [1]
2022-11-11 20:25:22 URL:https://quotes.toscrape.com/tag/life/page/1/ [12648/12648] -> "quotes.toscrape.com/tag/life/page/1/index.html.tmp.tmp" [1]
2022-11-11 20:25:22 URL:https://quotes.toscrape.com/tag/live/page/1/ [3942/3942] -> "quotes.toscrape.com/tag/live/page/1/index.html.tmp.tmp" [1]
2022-11-11 20:25:23 URL:https://quotes.toscrape.com/tag/miracle/page/1/ [3948/3948] -> "quotes.toscrape.com/tag/miracle/page/1/index.html.tmp.tmp" [1]
2022-11-11 20:25:24 URL:https://quotes.toscrape.com/tag/miracles/page/1/ [3950/3950] -> "quotes.toscrape.com/tag/miracles/page/1/index.html.tmp.tmp" [1]
...
```

The output needs a little cleanup, but essentially we are getting a list of pages on the site.
This can save your day if for some reason you cannot install hakrawler or similar tool when doing bounty hunting, but really
need some site crawled.

