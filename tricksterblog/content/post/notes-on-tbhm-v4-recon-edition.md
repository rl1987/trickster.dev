+++
author = "rl1987"
title = "Notes on TBHM v4 recon edition"
date = "2022-04-14"
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
target recon is conducted - we will have some initial questions that will branch out into further things
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
Each AS we find will have IP address ranges associated to it. However, if you do want 
to automate it Jason recommends the following tools:

* [ASNlookup](https://github.com/yassineaboukir/Asnlookup)
* [metabigor](https://github.com/j3ssie/metabigor)

Once we have some ASNs we can run [Amass](https://github.com/OWASP/Amass) in intel mode
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

There are plenty other sources to scrape target subdomains from. For example, to
enumerate Twitch subdomains with Google one might search for pages on initial domain
first, then use minus operator to exclude each new domain until there are no 
new domains found:

```
site:twitch.tv 
site:twitch.tv -www.twitch.tv
site:twitch.tv -www.twitch.tv -watch.twitch.tv
site:twitch.tv -www.twitch.tv -watch.twitch.tv -dev.twitch.tv
```

Furthermore, subdomains can be scraped from various sources by tools
like [Amass](https://github.com/OWASP/Amass) and [Subfinder](https://github.com/projectdiscovery/subfinder).
Amass can also link the subdomains it finds with Autonomous Systems,
which may provide new IP ranges to scan. 

You may also scrape Github API with script like [github-search](https://github.com/gwen001/github-search)
to dig up subdomains or source them from Shodan API with tool like
[shosubgo](https://github.com/incogbyte/shosubgo). This approach will require
you to get the relevant API keys and heed rate limits.

Lastly, one might monitor IP ranges of public cloud providers, looks
for servers that talk HTTPS and get domain names from their certificates. This
approach can be implemented by writing script that utilizes Masscan, but
Jason recommends [tls.bufferover.run](https://tls.bufferover.run/)
SaaS API that does this for you.

Besides subdomain scraping, there's subdomain bruteforcing, which is an activity
of automatically guessing subdomain names based on wordlist or by simply
iterating across character permutations. When bruteforcing, we check subdomain
guesses against real DNS servers. This can also be done with 
Amass. Another tool to do this is [Massdns](https://github.com/blechschmidt/massdns.git).
If you use a wordlist it is important to make sure that it is large enough.
There are multiple wordlists available on Github from red team/pentesting/
bug bounty space.

Sometimes subdomains you come across will have a pattern in their name, e.g.:

```
dev.company.com
dev1.company.com
dev2.company.com
```

[Altdns](https://github.com/infosec-au/altdns) is a tool developed to scan
for this kind of subdomains. Jason calls this technique "alteration scanning".
It can be used to find ways to bypass Web Application Firewall or the origin
server that is meant to be hidden behind the CDN.

When we have enumerated all the subdomains and Autonomous Systems, it is time to
do some port scannning. Jason recommends the following approach:

1. Run masscan to discover open ports on IP ranges. You may want to use wrapper
script to resolve domain names and scan IPs based on DNS responses, as 
masscan does not implement this on it's own.
2. Run Nmap service detection on masscan results. Output nmap results in a greppable
format.
3. Use [brutespray](https://github.com/x90skysn3k/brutespray) to check the above
for remote admin services that use default credentials.

Another thing we want to check is information leaks on Github. Like Google
and Shodan, Github can be searched with clever search queries to find things
relevant to security. Jason provides a simple [shell script](https://gist.github.com/jhaddix/1fb7ab2409ab579178d2a79959909b33)
that prints bunch of Github search links that you can check and also
recommends watching [GitHub Recon and Sensitive Data Exposure](https://www.youtube.com/watch?v=l0YsEk_59fQ)
from Bugcrowd University.

If you have a bunch of domains that may or may not have HTTP(S) services exposed
you may want to iterate across them and take screenshots of their front pages.
There are several tools for this:

* [Aquatone](https://github.com/michenriksen/aquatone)
* [HTTPScreenshot](https://github.com/breenmachine/httpscreenshot)
* [Eyewitness](https://github.com/FortyNorthSecurity/EyeWitness) - also provides server header info and some other intel.

This practice is known as "domain flyover".

Last thing to check are subdomain takeover opportunities. Subdomain takeover involves
finding a still valid CNAME DNS record for a subdomain that used to point to a third
party service, but no longer does and re-registering that service with the old subdomain
in order to cause some shenanigans (or to demonstrate the impact of security issue).  There's a Github 
repo called [can-i-take-over-xyz](https://github.com/EdOverflow/can-i-take-over-xyz)
that you may want to look into. [Nuclei](https://github.com/projectdiscovery/nuclei)
vulnerability scanner provides some automations (templates) to demonstrate this 
issue.

We have covered a lot of tools and techiques. Target recon can be a rather extensive process
and therefore it is highly desirable to automate as much of it as possible.
Many of the tools we have discussed are single threaded and do not take CIDR ranges or
file globs directly. [Interlace](https://github.com/codingo/Interlace) is a general 
purpose wrapper script that wraps simpler tools to make them effectively 
multithreaded in order to use them for larger scale recon operations.

When discussing further automation of recon process, Jason introduces the 
four levels of recon frameworks:

* C-level: basic Bash or Python scripts that glue together bunch of CLI tools.
* B-level: somewhat modular automation systems that runs point-in-time and
saves results into flat files. May have some GUI.
* A-level: fully modular automation systems with GUI that can continuously
monitor target systems. Has GUI and integrates a proper database.
* S-level: advanced automation systems that have all features in A-level with
scalability across multiple servers and AI/ML-based recon techniques.

See also:

* [Presentation slides](https://drive.google.com/file/d/1aG_qqRvNW-s5_8vvPk5rJiMSMeNL2uY9/view)
* [Visualisation by ceos3c](https://www.ceos3c.com/wp-content/uploads/2020/06/Bug-Hunter-Methodology-V4-Visualization.pdf)
* [DefCon Red Team Village workshop](https://www.youtube.com/watch?v=uKWu6yhnhbQ) - Jason goes through key steps of methodology and demonstrates the tooling.
* [How to shot web](https://www.youtube.com/watch?v=-FAjxUOKbdI) - a presentation at DEFCON back in 2015 that is predecessor of this methodology.

