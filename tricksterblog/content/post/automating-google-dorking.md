+++
author = "rl1987"
title = "Automating Google Dorking"
date = "2021-12-19"
draft = true
tags = ["automation", "python", "growth-hacking", "security", "bug-bounties"]
+++

There is more to using Google than searching by keywords, phrases and natural language questions. Google
also has advanced features that can empower users to be extra specific with their searches.

To search for exact phrase, wrap it in double quotes, for example:

```
"top secret"
```

To search for documents with a specific file extension, use `filetype:` operator:

```
filetype:pdf "top secret'
```

To search for results in specific domain, use `site:` operator. This can also be used with top level
domain, for example: 

```
site:gov filetype:pdf "top secret"
```

You may also watch to narrow down results based on part of URL that is not a domain name. This
can be achieved with `inurl:` operator:

```
site:gov inurl:declassified filetype:pdf "top secret"
```

Google also supports usage of Boolean operators in search queries, for example:

```
ethics AND (OSINT OR cybersecurity)
```

Google dorking is using advanced search queries to find finds that are not necessarily meant to be exposed
to the public internet. For example, to find some web cams, one might search:

```
intitle:"Live View/ — AXIS"
```

[Google Hacking Database](https://www.exploit-db.com/google-hacking-database) is a section of ExploitDB portal
that provides pre-written search queries that are meant to find things relevant for security. OSINT investigators
can use them to discover various pieces of information. Bounty hunters and penetration testers can use these 
queries as part of target recon phase. Likewise security professionals working on defensive side can also benefit
when evaluating the security of systems they are protecting. Some of these queries reveal plaintext passwords or
private keys.  I don't recommend using these for any malicious or questionable purposes, but if a site has a 
bug bounty program it might be worthwhile to report it.

WRITEME: introduce programmatic search API

WRITEME: discuss extra features that are only available on programmatic search

WRITEME: develop some example code that uses programmatic search

