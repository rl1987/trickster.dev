+++
author = "rl1987"
title = "Simple ways to find exposed sensitive information"
date = "2024-05-31"
draft = true
tags = ["scraping", "osint", "security"]
+++

Informational advantage is a form of power. On the flipside, exposure of sensitive
information about a person or organisation can be a privacy/security problem.
Sensitive Data Exposure is a type of vulnerability where software system (or 
user) makes sensitive data (API keys, user information, private documents, etc.) 
available to potential adversaries. For example, web app that lets users edit 
potentially confidential documents may be storing them in S3 buckets without
any proper access controls. This results in information that should not be
public being potentially available to those who know how to look for it. In this
post we will go through some basic techniques of Sensitive Data Discovery - 
the activity of hunting for accidental leaks of things that are best kept hidden.

One way to look for potentially sensitive information is to do search engine 
dorking - launching queries specifically crafted to narrow down on specific, 
potentially sensitive things. 

For example, the following query (Google dork) would look for PDF documents 
containing the word "confidential" and hosted under specific domain:

```
filetype:pdf site:hackerone.com "confidential"
```

We have used [`filetype:`](https://developers.google.com/search/docs/crawling-indexing/indexable-file-types#search-by-file-type)
operator to limit result to specific file extension and 
[`site:`](https://developers.google.com/search/docs/monitor-debug/search-operators/all-search-site)
operator to limit them to specific domain.

Of course, not every document containing word "confidential" is actually 
confidential, but a query like this could be a starting point to check if 
nothing sensitive is being leaked.

Another, more realistic example is the following Google query:

```
"contractors" filetype:xls "@gmail.com" site:gov
```

Automating Google dorking can be done via many of SERP scraper APIs available, 
but at the end of the day you will need to review the results manually.

On the very first page of search results I was able to find actual lists of 
government agency (e.g. Illinois Dept. of Transportation) contractors with email
addresses. Since pretending to be a contractor is very viable social engineering
vector that can lead to unauthorised access (physical and/or digital) to the 
sensitive infrastucture this sort of information exposure can have pretty serious
security implications. Furthermore, service-based businesses should take care 
not to expose their lead list spreadsheet on the public web as they can
potentially be found by some growth hacker working for the competition.

WRITEME: code-level searches on Github, PublicWWW, etc.

WRITEME: open S3 buckets

WRITEME: people not keeping their mouths shut on social media
