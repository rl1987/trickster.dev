+++
author = "rl1987"
title = "Strategies and patterns of gray hat social media automation"
date = "2022-04-25"
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
This may require reverse engineering API calls with tools like mitmproxy and perhaps even reverse engineering binaries
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
between them can be either undirected edges (e.g. Facebook friends) or directed edges (one account following or mentioning
another).

Social network analysis
-----------------------

From information gathered via social media scraping, we can model communities or audiences as graphs. By doing graph-theory
computations, we can get insights and ideas on how further growth hacking operations should be performed. Perhaps it is not desirable
to target major influencers or even their direct followers, but people connected indirectly to major influencer in a social graph
(e.g. followers of direct followers, but not direct followers themselves) would be the best audience to hit with automated
outreach. Merely plotting it with [NetworkX](https://networkx.org/) and matplotlib might provide some insight.

See the following examples:

* [Osintgram](https://github.com/Datalux/Osintgram) - tool to scrape Instagram for OSINT purposes.
* [youtube-dl](https://youtube-dl.org/) - tool to download videos from many sources, including social media platforms.
* [TWINT](https://github.com/twintproject/twint) - tool to scrape Twitter for OSINT.

In broader picture, social network analysis is entire branch of social science that deals with investigating communities
through the lens of graph theory. If we have social media footprint of some community scraped and stored in a database in
a structured way we can try to reverse engineer the social dynamics and use them to our benefit. 

Automating content creation
===========================

Automated social media accounts should have at least some content. There are are ways to automate content generation and/or
posting.

Recycling content
-----------------

If you have content created for one purpose or platform you can use automation to repurpose it for other platform, for example
by cutting up a longer video into shorter segments and uploading it to Tiktok for viewers with short attention span. 

Another approach is develop code to read RSS feeds of prominent news sources, use something like Bannerbear API to turn them 
into headline images and post them with link to original source.

Yet another way is to simply repost well performing content from other accounts. Many Instagram theme pages were build by 
doing exactly this - a practice known as "cash cow" pages.

AI-generated content
--------------------

At this point, AI systems such as GPT-3 can help with content creation, but not replace a human working at reasonable quality.
For example, one can use GPT-3 to generate Buzzfeed-style listicles, but to go beyond that you would need to get good
at prompt engineering - a practice of crafting good prompts that instruct the language model. That is a skill in itself.
However, AI systems can definitely make the content creation easier.

Spamming and manufacturing engagement
=====================================

Mass direct message sending
---------------------------

One spammy tactic is to send mass direct/private message to a pre-scraped list of potential customers. This is popular in NFT-related
communities on Discord. Whether or not it will annoy them is another matter.

Spammy engagement
-----------------

There are multiple way to nudge social media users into seeing our account:

* Liking their post.
* Commenting on their post.
* Mentioning their account.
* In some cases viewing their content (watching stories on IG or taking a look at LinkedIN profile of user with paid plan).

All of these tactics can be done with automation.

Instapy [quickstart script](https://github.com/InstaPy/InstaPy/blob/master/quickstart.py) provides a following example:

```python
session = InstaPy()

with smart_run(session):
    # general settings
    session.set_dont_include(["friend1", "friend2", "friend3"])

    # activity
    session.like_by_tags(["natgeo"], amount=10)
```

Follow-unfollow
---------------

If we want to collect a following of real people in our target niche it might be desirable to do follow-unfollow tactic that
entails automated following bunch of people within the niche every day, giving them a chance to follow our account and unfollowing
them if they don't reciprocate. This is fairly low cost way of not only bringing some traffic to the page, but also building
an audience over time. However, we cannot be too agressive with this as platform have rate limits on how many actions we can 
perform daily (although they change over time). Furthermore, it is desirable to keep your following-to-follower ratio as low
as possible, as it may become very obvious over time what we are doing here.

Risk management
===============

Using proxies
-------------

Generally speaking, one should use mobile 4G proxies for social media automation. Yes, that's expensive, but there are ways to
set them up with off-the-shelf hardware. In some cases residential proxies of sufficient quality are also enough.

You don't always want to use one proxy per account, but the amount of accounts sharing single exit IP should not be high.

Account pre-warming
-------------------

If you create or purchase an account you may not want to or be able to use it at full capacity from the beginning. You may need
to let it go through a pre-warming sequence, which entails gradually increasing activity on the account to make it less likely
to get banned and also to make social media platform increase the rate limits over time. This depends on exact social media platform,
account standing and what kind of automations are planned for the account.

Scraper accounts
----------------

API scraping entails making a lot of API calls to backend systems to extract information. If social media platform is prone to
cracking down on account based on this thing alone, it is desirable to have some accounts that are easily replaceable and meant
to act as cannon fodder while gathering information for further parts of automated workflow. These are called scraper accounts.

Mother-child method
-------------------

Due to automation countermeasures, it is highly desirable to refrain from running any sketchy automations on valuable accounts that
we are trying to establish as assets to make money long term. Yet it is still possible to use automation to grow these accounts 
through a technique called mother-child method. It is primarily used for growth on Instagram and uses 3 level-system of multiple
accounts:

1. Mother account that is not running any gray hat automations directly, but is used to build a primary audience and sell stuff.
2. Child accounts that perform things like follow-unfollow, mass DMs, etc. to bring new people to the mother account and maybe to
build secondary assets (that may be difficult because platform is likely to shut them down evenutally).
3. Scraper accounts that gather audience data for child accounts to act on. These are meant to be disposable and replaced when burned.

Abusing social media ads
========================

Targetting scraped audiences
----------------------------

PPC platforms such as Facebook ads allow you to import list of people (e.g. CSV file with column for emails) that are supposed to 
be your customers. This can be abused to run ads towards a scraped list of people and possibly save some money on advertisment.

Nanotargetting
--------------

Nanotargeting is a practice of using PPC ad platform to narrow down the ad targetting to very small number of people that we want
to influence, perhaps as little as one person. There's a [research](https://arxiv.org/pdf/2110.06636.pdf) finding that 
4 rarest Facebook interests of a person makes them unique in the user base with 90% probability. 

Manufacturing social proof
==========================

Fake followers
--------------

Bot or clickworker accounts can be used to artificially inflate the seeming popularity of social media account and fake social proof.

Fake engagement
---------------

Fake likes, comments and views can also be used to fake social proof.

Astroturfing
------------

Astroturfing is a practice that attempts to influence public discourse on product or public issue by having paid shills or 
bots post on public forums and social media platforms as if they were honest, concerned citizens or members of the community.

