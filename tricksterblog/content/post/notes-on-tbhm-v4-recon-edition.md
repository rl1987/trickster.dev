+++
author = "rl1987"
title = "Notes on TBHM v4 recon edition"
date = "2022-04-16"
draft = true
tags = ["security", "bug-bounties"]
+++

This post will summarize [The Bug Hunter's Methodology v4.01: Recon edition](https://www.youtube.com/watch?v=qLTe6Z10vj8) -
a talk at h@activitycon 2020 by Jason Haddix, a prominent hacker in the bug bounty community. Taking notes is important when 
learning new things and therefore notes were taken for future reference of this material. This methodology represents
breadth-first approach to bounty hunting and is meant to provide a reproducible strategy to discover as many assets 
related to the target as possible (but make sure to heed scope!). It will involve both OSINT and some active scanning
of web/IT systems.

Jason starts his talk by saying that you should takes notes during your recon activities as well. He uses [XMind](https://www.xmind.net/)
mind mapping tool to organise information being gathered, but pretty much anything that allows you to take notes and
organise them in a tree structure will do (Vim, spreadsheets, etc.). This way of taking notes mirrors the way
target reconnesaince is conducted - we will have some initial questions that will branch out into further things
we will need to look into to broaden our knowledge about the target.

The root element of tree for each project (e.g.  bounty program we are working on) should be marked with project name. This
root element will have two child nodes:

* Root/seed domains
* Recon

Under "Root/seed domains" we are going to put the initial domain names for bounty program that we find on e.g.
HackerOne program page when starting the process. Note that some bug bounty programs also include wildcard
entries such as `*.tesla.com` and may even say that any host verifiably owned by the company is in scope.
Thus we may need to do further research to enumerate an exact list of (sub)domains covered by a bounty
program.

Under "Recon" element we have some initial research questions that we will use
OSINT and other recon techniques to answer:

* ASNs - what autonomous systems does the company have?
* Acquisitions - what companies were acquired by company of interest?
* Linked discovery - what other assets can be found that are linked by and to company being looked into?
* Reverse whois - what domains belonging to a company can be found through a reverse whois tool?

Acquisitions are of interest to find new assets and seed/root domains as the systems formerly
belonging to acquired company now belong to the acquiring company, thus possibly falling into
the scope of a bug bounty program. Information on acquisitions can be found on sources such
as [Crunchbase](https://www.crunchbase.com/), Wikipedia or by simply Googling around.

Autonomous systems are large chunks or internet that are identified by Autonomous System
Numbers (ASNs) and are administered by large organisations. Huricane Electric provides
[BGP toolkit](https://bgp.he.net/) portal that we can use to try and find ASNs belonging to
a company we are looking into. Technically this can be scraped automatically but due to 
similarities between company names it's best to use human intelligence for this step.
Each AS we find will have IP address ranges associated to it. This will be useful in further
steps. However, if you do want to automate it Jason recommends the following tools:

* [ASNlookup](https://github.com/yassineaboukir/Asnlookup)
* [metabigor](https://github.com/j3ssie/metabigor)

Once we have some ASNs we can run [Amass](https://github.com/caffix/amass) in intel mode
to discover more seed domains.

Another way to discover more seed domains is to do reverse whois through something like
[Whoxy](https://whoxy.com/). We can do it manually through the web interface, but it
also has an API for intergration with our automations. [DOMLink](https://github.com/vysecurity/DomLink)
is one of the tools we can use to query Whoxy API for domain OSINT purposes.

Yet another thing that may help us discover assets related to a target is by linking
assets through ad pixels/analytics tracking codes. This can be done through
BuiltWith relationships pages, e.g.: https://builtwith.com/relationships/twitch.tv .

We can also use Google search with unique parts of legal pages (copyrights text, etc.)
to find more hosts/domains. Furthermore, searching for company name or primary domain
on [Shodan](https://shodan.io/) will reveal various assets related to the target.

Jason also recommends to use Burp Suite or other tool to discover (sub)domains by 
recursively crawling sites in a way that links are extracted not just from 
HTML pages but from JavaScript code as well. We would start with site(s) we already know
from seed domains and traverse links until we have no new subdomains left.
If you don't want GUI tool this can be done with [GoSpider](https://github.com/jaeles-project/gospider)
or [Hakrawler](https://github.com/hakluke/hakrawler). 

[Subdomainizer](https://github.com/nsonaniya2010/SubDomainizer)
will extract not only HTML and JS links from the page, but will also compute
Shannon entropy to find things that look like passwords or API keys. It will also
find things like S3 buckets being linked from the page. However this tool only works
on single pages. [Subscraper](https://github.com/Cillian-Collins/subscraper) is a similar
tool that also implements the crawling aspect.







