+++
author = "rl1987"
title = "How do they (try to) block bots: a broad review of automation countermeasures"
date = "2023-05-12"
draft = true
tags = ["security", "web-scraping", "automation"]
+++

Not every website wants to let the data to be scraped and not every app wants
to allow automation of user activity. If you work in scraping and automation 
at any capacity you certainly have dealt with sites that work just fine when 
accessed through normal browser throwing captchas or error pages at your bot. 
There are multiple security mechanisms that can cause this to happen. Today
we will do a broad review of automation countermeasures that can be implemented
at various levels.

IP level
========

The following techniques work at Internet Protocol level by allowing or blocking
traffic based on source IP address it is coming from.

Geofencing
----------

Geofencing (or geo-restricting/geo-blocking) is blocking/allowing requests
based on source geographic location (typically a country). This relies on GeoIP
data provided by vendors such as MaxMind or IP2Location to perform lookups.

As web scraper developer you can trivially bypass this using proxies.

Rate limiting
-------------

Web sites may impose upper bounds on on how many requests are allowed per some
timeframe from a single IP and start blocking incoming traffic if traffic
intensity exceeds that threshold. This is typically implemented with a leaky 
bucket algorithm. Suppose the site allows 60 requests per minute from a single
IP (i.e. one per seconds). It keeps a counter of how many requests it received,
decreasing it by one every second. If the counter exceeds the threshold value
(60) the site refuses further requests until it is below the threshold again.
This limits how aggressive we can be when scraping, but typically can be defeated
by spreading the traffic around a set of IP addresses by routing it through proxy
pool.

Filtering by AS/ISP
-------------------

This can be seen a variation of geofencing, but blocking can also be performed
based on source ISP or Autonomous System by performing Autonomous System
Lookups. For example, sites or antibot vendors may explicitly disallow traffic
that comes from data centers or major cloud vendors (AWS, Digital Ocean, Azure 
and so on).

Filtering by IP reputation
--------------------------

Proxies can be used to bypass the above ways to block traffic, but blocking
can also be performed based on IP address reputation data from threat 
intelligence vendors like IPQualityScore. So if your proxy provider is a 
sketchy one that is built on foundation of botnet it's proxies may be listed
in some blacklist, which makes the trust score bad. One must take care to use
a reputable proxy provider.

HTTPS level
===========

HTTP headers and cookies
------------------------

HTTP/2 fingerprinting
---------------------

TLS fingerprinting
------------------

Application level
=================

JS environment checking
-----------------------

Javascript challenges
---------------------

Browser and device fingerprinting
---------------------------------

User level
==========

CAPTCHA
-------

Account-level throttling
------------------------

Account banning
---------------

Mouse activity monitoring
-------------------------

Making account creation difficult
---------------------------------

