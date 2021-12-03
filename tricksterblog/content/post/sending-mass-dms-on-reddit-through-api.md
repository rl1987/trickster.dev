+++
author = "rl1987"
title = "Sending mass DMs on Reddit through API: a small experiment"
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
interface and takes care of OAuth flow for us. We will be using it for automation. It is available on PIP.

To set up the account for automation, we visit [apps section](https://old.reddit.com/prefs/apps/) of user preferences and press 
"create another app..." button. Then we choose "script" option, and enter some name and redirect URI into respective fields.
Don't worry too much about the redirect - I entered http://localhost and got no errors about it. Once you submit this form, 
you will get your API credentials. Client ID is the string under app name and Client Secret is available as well.

To access Reddit API through PRAW, one has to initialize a `Reddit` object first. The simplest way to do it is as follows:

```python
reddit = praw.Reddit(
    client_id="my client id",
    client_secret="my client secret",
    user_agent="my user agent",
    username="my username",
    password="my password",
)
```

However this entails hardcoding credentials into the Python script, which is generally a bad practice. We want to have a separate
configuration file for credentials that the code would read. PRAW let's us have a praw.ini file that can have contents like the 
following:

```
[bot]
client_id=[REDACTED]
client_secret=[REDACTED]
username=[REDACTED]
password=[REDACTED]
```

Once that is available in the same directory as our code, we can initialize the `Reddit` object like this:

```python
reddit = praw.Reddit("bot", user_agent="some user agent")
```

We only have to pass in the praw.ini file section name and PRAW will read credentials from that section.

To message some users, we first have to have a list of users to message. Thus we write a quick script that searches given
subreddits by a given search query.


TODO: write code for messaging users and explain it.

TODO: run some experiments and discuss results 

