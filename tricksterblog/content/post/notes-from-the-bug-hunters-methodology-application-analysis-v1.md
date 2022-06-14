+++
author = "rl1987"
title = "Notes from The Bug Hunters Methodology - Application Analysis v1"
date = "2022-06-14"
tags = ["security", "bug-bounties"]
+++

This post will consist of notes taken from [The Bug Hunter’s Methodology: Application Analysis v1](https://www.youtube.com/watch?v=HmDY7w8AbR4) - 
a talk by Jason Haddix at Nahamcon 2022. These notes are mostly for my own future review, but hopefully 
other people will find it useful as well.

Many people have been teaching how to inject an XSS payload, but not how to systematically find
vulnerabilities in the first place. Jason has created an AppSec edition of his methodology
when it became large enough to be split into recon and AppSec parts.

The following books are recommended:

* [The Web Application Hacker's Handbook 2](https://www.amazon.com/Web-Application-Hackers-Handbook-Exploiting/dp/1118026470/ref=sr_1_1?crid=223GVK9BGXP70&keywords=web+application+hackers+handbook+2&qid=1655126465&sprefix=web+application+hackers+handbook+2%2Caps%2C186&sr=8-1) - read this at least twice!
* [Real World Bug Hunting](https://www.amazon.com/Real-World-Bug-Hunting-Field-Hacking/dp/1593278616/ref=sr_1_1?crid=3MSIL2826QZGD&keywords=Real+World+bug+hunting&qid=1655126510&sprefix=real+world+bug+hunting%2Caps%2C160&sr=8-1)
* [OWASP Web Security Testing Guide](https://github.com/OWASP/wstg)
* [Bug Bounty Bootcamp](https://www.amazon.com/Bug-Bounty-Bootcamp-Reporting-Vulnerabilities/dp/1718501544)
* [The Hacker's Playbook 3](https://www.amazon.com/Hacker-Playbook-Practical-Penetration-Testing/dp/1980901759/ref=sr_1_1?crid=IPJY7MVTIQO8&keywords=the+hackers+playbook+3&qid=1655126695&s=books&sprefix=the+hackers+playbook+3%2Cstripbooks%2C156&sr=1-1)
* [Breaking into information security](https://www.amazon.com/Breaking-into-Information-Security-Crafting-ebook/dp/B019K7CMMW/ref=sr_1_1?crid=AOOXS637SAU4&keywords=breaking+into+information+security&qid=1655126724&s=books&sprefix=breaking+into+information%2Cstripbooks%2C167&sr=1-1)
* [Hands on Hacking](https://www.amazon.com/Hands-Hacking-Matthew-Hickey/dp/1119561450/ref=sr_1_1?crid=W4KBT61E7RQ5&keywords=Hands+on+hacking&qid=1655126763&s=books&sprefix=hands+on+hacking%2Cstripbooks%2C159&sr=1-1)
* [Bug Bounty Playbook](https://payhip.com/b/wAoh) - similar to Jason's methodology.

The following resources are recommended for practice:

* [PentesterLab](https://pentesterlab.com/) - paid
* [Web Security Academy](https://portswigger.net/web-security) - paid
* [Hack The Box](https://www.hackthebox.com/) - paid
* [Vulnhub](https://www.vulnhub.com/) - free
* [OWASP Vulnerable Web Application Directory](https://owasp.org/www-project-vulnerable-web-applications-directory/) - free

The free ones also are good to practice some sysadmin stuff, as you're supposed to know that as well for bounty hunting.

Recommended security content creators to follow:

* @danielmiessler [Twitter](https://twitter.com/danielmiessler) [Podcast](https://danielmiessler.com/podcast/)
* @stok [Twitter](https://twitter.com/stokfredrik) [Youtube](https://www.youtube.com/c/STOKfredrik)
* @brutelogic [Twitter](https://twitter.com/brutelogic) [Blog](https://brutelogic.com.br/blog/)
* @InsiderPhD [Twitter](https://twitter.com/InsiderPhD) [Youtube](https://www.youtube.com/c/InsiderPhD)
* @infosec_au [Twitter](https://twitter.com/infosec_au) [Blog](https://blog.assetnote.io/)
* @Farah_Hawaa [Twitter](https://twitter.com/Farah_Hawaa) [Youtube](https://www.youtube.com/c/farahhawa)
* @zseano [Twitter](https://twitter.com/zseano) [Youtube](https://www.youtube.com/c/zseano)
* @hacker_ [Twitter](https://twitter.com/hacker_) [Blog](https://corben.io/)
* @hakluke [Twitter](https://twitter.com/hakluke) [Blog](https://hakluke.com/blog/)
* @albinowax [Twitter](https://twitter.com/albinowax) [Blog](https://skeletonscribe.net/)
* @tomnomnom [Twitter](https://twitter.com/tomnomnom) [Youtube](https://www.youtube.com/user/TomNomNomDotCom/featured)
* @\_JohnHammond [Twitter](https://twitter.com/_JohnHammond) [Youtube](https://www.youtube.com/johnhammond010)
* @ippsec [Twitter](https://twitter.com/ippsec) [Youtube](https://www.youtube.com/c/ippsec)
* @nahamsec [Twitter](https://twitter.com/nahamsec) [Youtube](https://www.youtube.com/c/nahamsec)

Generally there's a lot of bounty hunting community on Twitter.

Don't be intimidated by bug bounty programs by high profile companies as they have a lot of systems online that are bound
to have things you can find. More complexity and scale - more opportunity for bugs. The same applies to bounty programs
that involve pre-testing before they are publically available, open source projects and paid software products. 
There are bugs in every application.

Don't merely touch the surface of the app - most of the good stuff is to be found beyond the authentication.

There are following layers to security testing:

* Open ports and services
* Web hosting software
* Application framework
* Application: custom code
* Application libraries
* Integrations

We need to do technology profiling first. The following browser extensions can be used to find 
what technologies site is based on:

* [Whatruns](https://www.whatruns.com/)
* [Wappalyzer](https://www.wappalyzer.com/)

There is also [webalyze](https://github.com/rverton/webanalyze) - a CLI tool that can be integrated into automated scanning pipelines.

Now it's time to check that no known vulns, default credentials, framework login pages and the like are 
present on the site (related to non-custom code). This can be done with Nuclei or Nessus.
Nuclei has plenty of checks for CVEs, admin panels, information leaks and the like. 
There's other tools for this:

* [Gofingerprint](https://github.com/Static-Flow/gofingerprint)
* [Sn1per](https://github.com/1N3/Sn1per)
* [Intrigue Core](https://core.intrigue.io/)
* [Vulners](https://vulners.com/plugins#burp) (Burp extension)
* [Jaeles](https://github.com/jaeles-project/jaeles)
* [retire.js](https://github.com/retirejs/retire.js/)

However, overreliance on Nuclei can be a competitive disadvantage if it is being used
to scan what everyone else is scanning - you are merely going to find dupes. But you
can still find vulnerabilities if you use Nuclei for fresh or obscure targets.
Nuclei templates are very easy to write which enables you to start using it to find
newly published vulnerabilities.

You also want to do some port scanning. Jason recommends [naabu](https://github.com/projectdiscovery/naabu) by Project Discovery.
It can be integrated with Nmap for service scanning.

Next phase is content discovery. This is very important part that has several sections:

* Tech-based discovery
* COTS / PAID / OSS
* Custom
* Historical
* Recursive
* Mobile APIs
* Change Detection

The following tools are recommended for content discovery:

* [Turbo Intruder](https://portswigger.net/bappstore/9abaa233088242e8be252cd4ff534988) (Burp extension)
* [Gobuster](https://github.com/OJ/gobuster)
* [ffuf](https://github.com/ffuf/ffuf)
* [Feroxbuster](https://github.com/epi052/feroxbuster)
* [dirsearch](https://github.com/maurosoria/dirsearch)
* [Wfuzz](https://github.com/xmendez/wfuzz)

These will be used to bruteforce/fuzz directories on web servers to discover stuff.
Gobuster can also find subdomains and S3 buckets.

It is also important to have pre-made lists for content discovery to look for common
things likes swagger.json file and various web-server or framework specific directories.
Sometimes this lets us find unprotected configuration files with database credentials
and other sensitive information. There are some lists available that are based on e.g.
scraping robots.txt files from most popular sites and compiling a big list of things
that sites don't want bots to acesss/index. Some lists are technology-specific, i.e.
to be used against PHP or Java sites, some are generic. Make sure to you an up-to-date
list. See: https://wordlists.assetnote.io/

If an application is built on open source stuff you can use 
[Source2URL](https://github.com/danielmiessler/Source2URL/blob/master/Source2URL) - 
a Bash script that goes through source code, harvests URLs and tries to access them through
proxy (e.g. Burp). 

But what if it's a paid that that is being deployed (e.g. some CRM solution)? In that
case you may be able to get access by contacting the paid software vendor and get a
demo access by pretending to be interested in buying it. This will enable you to 
explore the paid software and note down various API endpoints and other URL paths
to make your own wordlist for content discovery. This custom list would be then
used against an actual target.

Custom content discovery lists can be also built by spidering sites and using 
Scavenger in Burp to make the list for you.

Content discovery lists can also be built from historical data. 
[gau](https://github.com/lc/gau) is a tool that will access Open Threat Exchange,
Wayback Machine and CommonCrawl for a list of URLs to all known historical 
pages on the site. Output of this tool can be fed into 
[wordlistgen](https://github.com/ameenmaali/wordlistgen) to make a wordlist
based on list of URLs. For some sites gau will yield a lot of duplicate entries
that can be cleaned up with [trashcompactor](https://github.com/michael1026/trashcompactor).

Recursive bruteforcing should be used on URL paths that yield HTTP 401 response,
as if you go deep enough you may find some level that does not enforce authentication
due to misconfiguration and then you're in. Jason mentions finding a massive
amount of unprotected private data and access to SMS panel by doing recursive
content discovery.

Many times same domain is used for mobile API as well, which means that mobile
API endpoints are covered by bug bounty program. They can be discovered by
parsing APK file with tool like [APKLeaks](https://github.com/dwisiswant0/apkleaks).
This will also look for hardcoded API keys and other things that may be useful
for further analysis.

Another tip is to monitor for website changes by using tools like
[ChangeDetection](https://github.com/dgtlmoon/changedetection.io).
Another ways to find about changes is signing up for affiliate program,
watching the conference talks by company that develops the app in question,
reading their email newsletter. In bounty hunting it is of importance to be
the first to find new vulnerabilities ASAP after the code has changed.

Next stage is application analysis.

There are 6 highly important questions to ask when it comes to app analysis.

1. How does it pass data? Is it by resource and URL parameters or is it
a combination of HTTP method and URL path? Not getting this right may derail
your further fuzzing/scanning efforts.

2. Where and how does it reference users? How are they identified (UUID, user ID,
email, something else?) and where is the identifier communicated? Does it 
enforce consistency between session and user?

3. Does it have multi-tenancy or multi-user functionality? This would have
potential for access, authentication and authorization bugs as it's very
hard for developers to enforce boundaries properly in all cases. This
can  yield IDORs, information disclosure bugs and so forth. Are there 
different levels of permissions within the app? Are there ways for lower
level user to view information that only admin is supposed to access?

4. Does the site have unique threat model? For example, securing
stream keys and private streamer information is very important for
Twitch, as leaking this data may lead to all kinds of trouble.
This also applies to medical sites.

5. Has there been prominent examples of vulnerabilities and attacks
against the system being analysed? Just Google for this.

6. How does the app and/or framework handle XSS, CSRF and injection
attacks? What are countermeasures like and how can they be bypassed?

Spider the site to ensure coverage with something like Burp or ZAP.
You need to cover as many code paths as possible. Alternatively,
you can use [hakrawler](https://github.com/hakluke/hakrawler) 
or [GoSpider](https://github.com/jaeles-project/gospider) for GUI-less automation.

You may also want to parse JavaScript code to find sensitive API endpoints
and maybe even API keys with tool like 
[xnLinkFinder](https://github.com/xnl-h4ck3r/xnLinkFinder). There's also Burp
extension for that.

Sometimes JS code will be minified or obfuscated, but will still contain
things to be find there. 

Sometimes old JS libraries will be used and will contain exploitable
vulnerabilities. This can be found with retire.js.

Heat mapping is an idea that there are certain places in the app
that are of particular interest or potential for bugs:
upload functions, integrations with 3rd parties, external
data storage (e.g. in S3 bucket), multipart forms, account sections,
APIs and error pages. 

Few years ago there was research project (HUNT) to determine what URL parameters
tend to statistically correlate with specific types of vulnerabilities.
This provides a good idea on what to check first and prioritise 
parameters/routes in terms of their potential for bugs.
There's a [Burp extension](https://github.com/bugcrowd/HUNT) that helps with this.

