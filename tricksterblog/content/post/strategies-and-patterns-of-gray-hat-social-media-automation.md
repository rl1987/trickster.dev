+++
author = "rl1987"
title = "Strategies and patterns of gray hat social media automation"
date = "2022-04-24"
draft = true
tags = ["web-scraping", "python", "growth-hacking"]
+++

Introduction and motivation
===========================

We live in the postmodern age of hyperreality. Vast majority of information most people receive through technological
means without having any direct access to it's source or any way to verify or deny what is written or shown on the screen.

A pretty girl sitting in a private jet might have paid a lot of money to fly somewhere warm or might have paid a [company](https://www.privatejetphotoshoot.com/)
that keeps the plane on the tarmac smaller amount of money to do a photo shoot. Her fans on Instagram have no idea which of these
scenarios is true simply from seeing the picture of her relaxed in fancy seat, looking into distance through her sunglasses 
and sipping wine. That's hyperreality. The same applies to supposedly very successful twenty-something guy in an expensive car
that may or may not have been rented for a day to make an entire months worth of pictures.

In modern information society, attention is money. There are multiple ways to financially benefit from peoples attention
through PPC advertisements, sponsorships, affiliate deals, promoting your own products or by simply selling your audiences
attention to the highest bidder (influencer marketing). Some people have become millionaires or even billionaires by
being able to play the social media game very well. Hyperreality is particularly prevalent on modern social media platforms 
that are deliberately engineered to extract as much time and attention (engagement) from it's users as possible, then
sell it through the integrated ad platform to the highest bidder. Objective truth be damned, Big Social executives will
do anything to keep the people reading, clicking, watching. Large scale virtual reality as it was imagined by science
fiction writers and technologists in 80s and 90s did not happen yet, but virtual *social* reality is already here.

If Big Social business objectives require, the organic reach is deliberately being limited to make more spaces for paid ads. 
Therefore promoting your brand on major social media platforms by playing it straight and relying on organic reach only 
works up to a point. It is still feasible on Tiktok, but less and less viable on Instragram and Facebook. The same applies
to buying peoples attention on social media ad platforms such as Facebook. When social media ad spend is overall increasing
auctions for human attention are getting more and more competitive, thus many business are finding that they are being priced out.
In 2022, it is very easy to burn bunch of money on e.g. Facebook ads only to end up net negative by the end of the quarter.

So if we simply want to make some money, how do we proceed in this crazy world? If Big Social takes away the organic
reach with one hand and charges more and more money for paid ads with another how do we turn a profit? 

One of the feasible answers is growth hacking through gray hat social media automation. Let me elaborate what I mean by 
that. Growth hacking is a kind of marketing that focuses on low-cost, experimental, unorthodox ways to get new customers 
and retain them. Social media automation is use of programmatic techniques and software tools to mainly do things that
some social media manager would be doing manually. In the order of increasing sketchiness, we classify the automation
techniques into three levels:

1. White hat - fully legitimate and T&C-compliant automation, such as posting stuff on schedule through Buffer, ToS-compliant
chatbots and so on. Legit stuff in the eyes of social media platform that nobody would legitimately complain about.
2. Gray hat - automations that explicitly break T&C of social media platform. Somewhat sketchy stuff.
3. Black hat - automations for malicious and criminal purposes, such as phishing, harassment or mass-reporting social
media accounts on fraudulent basis. The evil stuff.

Assuming we don't want to play the dangerous game of truly black hat automation on moral and risk management grounds, why
do we pick the gray hat option? Why not go with white hat automation and do everything in entirely clean way? Well, frankly
that's because white hat automation has no teeth in 2022. We would be merely making an improvement over manual social
media management, but not going far beyond that. Altough Big Social is proactively working against non-whitehat automation 
on technical and legal levels, gray hat automation at least gives us a fighting chance when trying to monetise these
massives audiences on modern massive social networks.

Gray hat social media automation is not an easy thing to do in the post-Cambridge Analytica world, but may provide something
like a cheat code to those trying to make money online. Gray hat automation attempts to turn the tables against Big Social
by exploiting the very state of manipulative data-driven hyperreality that the Zuckerbergs of the world have created.

Like in object-orient programming, there are patterns - abstract principles of doing things that keep popping up when one 
works in the field or is researching it. We will discuss the patterns of gray hat social media automation that are more 
or less applicable to multiple platforms and can be thought of as theorethical concepts without scrutinizing how exactly 
they would be implemented.

But refrain from implementing some equivalent of [FizzBuzz Enterprise Edition](https://github.com/EnterpriseQualityCoding/FizzBuzzEnterpriseEdition) 
if you can.

Two major approaches
====================

Broadly speaking, scraping HTML pages and submitting forms via POST requests is not how social media automation is done
in modern times. There are two major technical approaches to implement gray hat automations for social media. Both of these
must deal with automation countermeasures that platforms implement.

(Ab)using platform APIs
-----------------------

One approach is automating against platform APIs. To some extend this can be possible through public APIs described on the
developer portal documentation (this was how [Howitzer](https://howitzer.co/) worked originally), but primarily we would
need to pretend to be a mobile app or frontend JavaScript code of social media platfrom and reproduce private API calls.
This may require some reverse engineering with tools like mitmproxy and perhaps even reverse engineering binaries
of mobile apps if API security techniques such as request signing with HMAC is used. We may need to deal with complex
API flows, such as Instagram [using](https://stackoverflow.com/questions/62436766/cant-login-to-instagram-using-requests) 
AES256 in GCM mode to encrypt the password during login.

Browser automation
------------------

Another approach is running an entire browser and controlling it programmatically. In some cases browser is running in
headless mode - without the GUI window. There's several ways to do this. One is implementing basic bots that automation
user could install as browser extensions. Another is using browser automation technologies such as Selenium, Playwright
or Puppeteer to develop scripts implementing the automations. On surface this may seem to be easier than API-based automation,
but it entails the risk of detection due some tell-tale signs in the JS environment, as browser being automated will not
behave exactly the same way as browser being user by a real user. [InstaPy](https://github.com/InstaPy/InstaPy) is a
prominent open source project to implement IG automations by controlling the browser with Selenium.

Account creation
================

Being able to quickly and automatically create social media accounts is highly beneficial for growth hacking. It entails
automating registration flow with the help of proxies, captcha solvers and - if phone verification is requeired - 
SMS reception services such as [SMSPVA](https://smspva.com/) or [Valar SMS](https://valar-sms.com/) or your own setup,
such as phone farm or product like [Proxidize](https://proxidize.com/) that can also be used to receive text messages for
verification.

Scraping and data analysis
==========================

Social media scraping
----------------------

Social media platforms can be scraped just like any other website, but it is generally more difficult due to automation
countermeasures and many pages generally being behind login. It is advisable to take a look into Network tab in Chrome 
DevTools as sometimes information not visible on the frontend is available in API responses, such as email addresses 
for some business Instagram accounts.

Scraping social media pages can yield not only some contact information to be used later, but can also help to map out
communities in graph-theorethical way. Speaking in graph theory terms, a social media profile is a vertex and connections
between them can be either undirected edges (e.g. Facebook friends) or directed edges (on account following or mentioning
another).

Social network analysis
-----------------------

From information gathered via social media scraping, we can model communities or audiences as graphs. By doing graph-theory
computations, we can get insights and ideas on how further growth hacking operations should be performed. Perhaps it is not desirable
to target major influencers or even their direct followers, but people connected indirectly to major influencer in a social graph
(e.g. followers of direct followers, but not direct followers themselves) would be the best audience to hit with automated
outreach. Merely plotting it with [NetworkX](https://networkx.org/) and matplotlib might provide some insight.

In broader picture, social network analysis is entire branch of social science that deals with investigating communities
through the lens of graph theory. If we have social media footprint of some community scraped and stored in a database in
a structured way we can try to reverse engineer the social dynamics and use them to our benefit. 

Spamming and manufacturing engagement
=====================================

Mass direct message sending
---------------------------

Spammy engagement
-----------------

Follow-unfollow
---------------

Risk management
===============

Using proxies
-------------

Account pre-warming
-------------------

Scraper accounts
----------------

Mother-child method
-------------------

Abusing social media ads
========================

Targetting scraped audiences
----------------------------

Nanotargetting
--------------

