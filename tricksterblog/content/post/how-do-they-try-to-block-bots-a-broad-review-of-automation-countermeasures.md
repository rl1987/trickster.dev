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

Geofencing
----------

Rate limiting
-------------

Filtering by AS/ISP
-------------------

Filtering by IP reputation
--------------------------

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

