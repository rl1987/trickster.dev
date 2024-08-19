+++
author = "rl1987"
title = "Katana: web crawler for offensive security"
date = "2024-08-31"
tags = ["security"]
draft = true
+++

[Katana](https://github.com/projectdiscovery/katana) is CLI tool and Go library
for automatically traversing (crawling) across all pages of given website(s) to
map them out. It can work in two main modes - requests-based and through browser
automation (headful or headless). To allow for discovery of API endpoints it 
can optionally do JavaScript parsing even when running in requests-based mode.
Furthermore, Katana can do passive crawling by leveraging pre-crawled data from
Internet Archive Wayback Machine, CommonCrawl and Alien Vault OTX.
Since mapping out site pages and APIs is useful for security research activities
(e.g bug bounty hunting) Katana is designed to fit into larger automation 
workflows, esp. when used together with other tooling from Project Discovery.

If we simply want to see a list of pages a site has we only have to pass the 
site URL via `-u` parameter:

```
$ katana -u https://public-firing-range.appspot.com/

   __        __                
  / /_____ _/ /____ ____  ___ _
 /  '_/ _  / __/ _  / _ \/ _  /
/_/\_\\_,_/\__/\_,_/_//_/\_,_/							 

		projectdiscovery.io

[INF] Current katana version v1.1.0 (latest)
[INF] Started standard crawling for => https://public-firing-range.appspot.com/
https://public-firing-range.appspot.com/
https://public-firing-range.appspot.com/vulnerablelibraries/index.html
https://public-firing-range.appspot.com/stricttransportsecurity/index.html
https://public-firing-range.appspot.com/urldom/index.html
https://public-firing-range.appspot.com/reverseclickjacking/
https://public-firing-range.appspot.com/reflected/index.html
https://public-firing-range.appspot.com/mixedcontent/index.html
https://public-firing-range.appspot.com/tags/index.html
https://public-firing-range.appspot.com/redirect/index.html
https://public-firing-range.appspot.com/remoteinclude/index.html
https://public-firing-range.appspot.com/insecurethirdpartyscripts/index.html
https://public-firing-range.appspot.com/leakedcookie/index.html
https://public-firing-range.appspot.com/flashinjection/index.html
https://public-firing-range.appspot.com/vulnerablelibraries/jquery.html
...
```
