+++
author = "rl1987"
title = "Simple ways to find exposed sensitive information"
date = "2024-05-31"
draft = true
tags = ["scraping", "osint", "security"]
+++

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

Of course, not every document containing word "confidential" is actually 
confidential, but a query like this could be a starting point to check if 
nothing sensitive is being leaked.


WRITEME: code-level searches on Github, PublicWWW, etc.

WRITEME: open S3 buckets

WRITEME: people not keeping their mouths shut on social media
