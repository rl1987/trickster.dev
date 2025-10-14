+++
author = "rl1987"
draft = true
title = "Scraping Next.js pages in 2025"
date = "2025-10-31"
tags = ["scraping"]
+++

When looking into some targets for web scraping, you may come across pages
that contain a lot of data represented in JSONesque (but not quite JSON) format
passed to `self.__next_f.push()` Javascript function calls. What's going on 
here and how do we parse this stuff? To understand what this is about, we must
go through a little journey across the technological landscape of the modern
web.

* React and Next.js
* `__NEXT_DATA__`
* `self.__next_f.push` / Next.js flight data
* njsparser

