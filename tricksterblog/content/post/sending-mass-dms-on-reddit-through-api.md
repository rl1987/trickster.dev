+++
author = "rl1987"
title = "Sending mass DMs on Reddit through API"
date = "2021-12-05"
draft = true
tags = ["automation", "growth-hacking", "python"]
+++

[Howitzer](https://howitzer.co/) is a SaaS tool that scrapes subreddits for users mentioning given keywords and automates mass
direct message sending for growth hacking purposes. 

Generally speaking, there are significant difficulties when automating against major social media platforms. However, Reddit
is not as hostile towards automation as other platforms and even provides a relatively unrestricted 
[official API](https://www.reddit.com/dev/api/) for building bots and integrations.

Let us try automating against Reddit API with Python to build a poor mans Howitzer with Python.

Before we start, it is important to have a pre-warmed/pre-used account that we're willing to burn. The I got one from 
[Accfarm](https://accfarm.com/buy-reddit-accounts/softreg-reddit-accounts) has over 1000 karma (I paid close to
$40 for it). Reddit will not allow DM'ing users if the account is freshly created.

[PRAW](https://praw.readthedocs.io/en/stable/index.html) is a Python module that wraps Reddit API calls into Pythonic
interface and takes care of OAuth flow for us. We will be using it for automation.

TODO: write code for scraping users and explain it.

TODO: write code for messaging users and explain it.

TODO: run some experiments and discuss results 

