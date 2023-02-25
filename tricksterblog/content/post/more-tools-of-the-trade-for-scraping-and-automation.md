+++
author = "rl1987"
title = "More tools of the trade for scraping and automation"
date = "2022-07-26"
tags = ["automation", "scraping"]
+++

Since the [previous post](/post/tools-of-the-trade-for-scraping-and-automation)
I realised that there's more interesting and valuable tools that were not covered
and that this warrants a new post. So let's discuss several of them.

[AST Explorer](https://astexplorer.net/)
========================================

Sometimes you run into obfuscated code that you need to make sense of and write
some code to undo the obfuscation. AST explorer is a web app that let's you put
in code snippets and browse the AST for multiple programming languages and
parsing libraries. For some of the languages it is even possible to apply
AST-level transformations to prototype things like deobfuscation techniques.

[AppSmith](https://www.appsmith.com/)
=====================================

AppSmith is a low-code, self hostable platform for creating internal dashboards
for people who would rather not do frontend programming. If you have written
some code that deals with data and automation AppSmith will provide a way to
drag-and-drop some frontend web UI from existing widgets, as well as customise
it with JavaScript. There's many integrations for databases and external APIs
for building simple internal CRUD apps.

[Burp Suite](https://portswigger.net/burp)
==========================================

Burp is a widely known interception proxy that is highly popular in the
bug bounty community. Think of it as mitmproxy on steroids - not only it can
intercept HTTP messages for inspection, but also allow you to do things like
catching a request and modifying it in flight, running directory enumerations,
bruteforce attacks and much more. Altough Burp is a GUI app largely written in
Java it is possible to extend it with your own plugins that can be developed
in Python.

There's multiple editions of Burp, but the free Community Edition is a good
starting point.

[GAU](https://github.com/lc/gau)
================================

GAU (Get All Urls) is a command line tool for fetching a list of known URLs
for a given domain from several sources (Wayback Machine, Common Crawl and some 
others). This can be useful when exploring the site before developing scraper code
or when doing recon for bounty hunting purposes.

[Mautic](https://www.mautic.org/)
=================================

Mautic is an open source email marketing solution that you can self host to
run your own email campaigns. It has a REST API that enable integration
with other stuff for list building and transactional emails. Mautic supports 
many things that email marketing / cold outreach SaaS solutions do, such as
A/B testing, drip campaigns, personalisation, sending emails based on triggers
and so on. Furthermore, it has ready-made integrations with multiple email
service providers, such as AWS SES and SendGrid.

If you are doing gray hat growth hacking, such as cold-emailing a scraped list
of companies or individuals there's an argument to be made in favour of self-hosting
your stuff to pre-empt the potential problem of email SaaS vendor you are using
cutting you off.

[Insomnia](https://insomnia.rest/)
==================================

Insomnia is a GUI app that lets you interact with REST APIs. It can take a curl
snippet, break it down it request components, let you edit the request to
experiment with the API and regenerate either Bash snippet that relies on curl
or code snippet in one of the several programming languages. Furthermore, Insomnia
has features for designing and testing your own APIs.

[PublicWWW](https://publicwww.com/)
===================================

PublicWWW is a code-level search engine that lets you search the web based
on things like JS file names, HTML fragments, variable names, HTTP headers 
and so on. Unfortunately the free version does not give you all the
data, but the paid version is only accessible through Tor Onion Service and the
only way to pay them is through Bitcoin. This is rather weird and I suspect
the developers of this thing are evading sanctions. However the tool itself
has some value if you are looking to search the web in a deeper way than it
is possible with regular search engines. For your convenience, results
can be exported as CSV and you can even use regular expression when searching
for something. For example, the following query would give you list of Wordpress
plugins being deployed on various websites:

```
"/wp-content/plugins/" snipexp:|/plugins/([\w\d\-\.\_]+)/|
```

[Visidata](https://www.visidata.org/)
=====================================

If you are running your scrapers on servers without any GUI environment it might
be a hassle to download CSV files or spreadsheets to check the data that
was scraped. This is where Visidata comes in. Visidata is a terminal-based
tool to view and analyse tabular data that even supports basic data visualisations
such as frequency histograms and scatterplots. Since this tool is written in
Python it can be installed through PIP.

[Wireshark](https://www.wireshark.org/)
=======================================

Wireshark is a prominent packet sniffer that lets you see what exactly happens
in the network. It can be used for things like troubleshooting proxy issues
and other network-related stuff, as well as for getting a deeper insight into
how networked software is truly operating.

