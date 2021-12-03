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
subreddits by a given search query and saves the results into CSV file.

```python
#!/usr/bin/python3

import csv
from datetime import datetime
from pprint import pprint
import sys

import praw

USER_AGENT = "automations"

FIELDNAMES = [ "subreddit", "username", "title", "selftext", "datetime" ]
OUTPUT_CSV_PATH = "posts.csv"

def iso_timestamp_from_unix_time(unix_time):
    dt = datetime.fromtimestamp(unix_time)
    return dt.isoformat()

def scrape_subreddit(reddit, query, subreddit_name):
    sr = reddit.subreddit(display_name=subreddit_name)

    for s in sr.search(query, limit=None):
        row = {
            "subreddit": subreddit_name,
            "username" : s.author.name,
            "title": s.title,
            "selftext": s.selftext.replace("\n", " "),
            "datetime": iso_timestamp_from_unix_time(s.created_utc),
        }

        yield row

def main():
    if len(sys.argv) != 3:
        print("{} <query> <subreddit1,subreddit2,...>".format(sys.argv[0]))
        print("Use subreddit names with /r/ - e.g. 'webscraping', not '/r/webscraping'")
        return

    query = sys.argv[1]
    subreddit_names = sys.argv[2].split(",")

    reddit = praw.Reddit("bot", user_agent=USER_AGENT)

    out_f = open(OUTPUT_CSV_PATH, "w", encoding="utf-8")

    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()

    for subreddit_name in subreddit_names:
        for row in scrape_subreddit(reddit, query, subreddit_name):
            pprint(row)

            csv_writer.writerow(row)

    out_f.close()
    
if __name__ == "__main__":
    main()
```

As you can see, PRAW module nicely wraps Reddit API into object-oriented Python and makes things fairly easy for us.

When we run this, we get a CSV file with rows similar to the following:

```
subreddit,username,title,selftext,datetime
webscraping,Raghu1990,Can I scrape price target history from marketbeat.com ? Preferably using python.,,2021-11-27T00:50:17
webscraping,omarsika,How to access all data from api jQuery using python?,"Help please, I have this url here that I need to scrape for an assignment [https://www.lesmiraculeux.com/pages/store-locator](https://www.lesmiraculeux.com/pages/store-locator)  I was able to get this get request from Postman, but no matter how much I play around with the parameters or headers I can only get 100 results.   Here is the callback function settings - [https://stockist.co/api/v1/u8403/widget.js?callback=\_stockistConfigCallback](https://stockist.co/api/v1/u8403/widget.js?callback=_stockistConfigCallback)  Best I was able to do was input a list of coordinates and dedupe, is there a way to get the jQuery to return all the results instead of just 100?  Thank you!    > url = ""https://stockist.co/api/v1/u8403/locations/search?callback=jQuery&tag=u8403&latitude=48.88936919246074&longitude=2.3697855000000168""            payload={}      headers = {            'authority': 'stockist.co',            'sec-ch-ua': '""Google Chrome"";v=""95"", ""Chromium"";v=""95"", "";Not A Brand"";v=""99""',            'sec-ch-ua-mobile': '?0',            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',            'sec-ch-ua-platform': '""Windows""',            'accept': '*/*',            'sec-fetch-site': 'cross-site',            'sec-fetch-mode': 'no-cors',            'sec-fetch-dest': 'script',            'referer': 'https://www.lesmiraculeux.com/',            'accept-language': 'en-US,en;q=0.9'}          response = requests.request(""GET"", url, headers=headers, data=payload)       data = response.content[11:-2]      stores = {'name':[], 'address':[],'zipcode':[],'city':[], 'lat':[],'long':[]}      for i in json.loads(data)['locations']:              stores['name'].append(i['name'])              stores['address'].append(i['address_line_1'])              stores['zipcode'].append(i['postal_code'])              stores['city'].append(i['city'])              stores['lat'].append(i['latitude'])              stores['long'].append(i['longitude'])            df = pd.DataFrame(stores)      df.head()",2021-11-27T21:48:42
...
```

We purposely include data about the post as we want to be able to evaluate data quality for growth hacking purposes. However, to
send direct messages only the second column is needed. Thus we run the following command on Unix (macOS in this case) to extract
it:

```
cat posts.csv | tail -n +2 | awk -F "," '{ print $2 }' | sort | uniq > users.txt 
```

Note that sort(1) has to be just before uniq(1) in the pipeline. Duplicate username filtering will not work otherwise.

The code to mass DM the Reddit users is as follows:

```python
#!/usr/bin/python3

import time

import praw
import prawcore

USER_AGENT = "automations"

def try_posting(reddit, username, subject, message):
    try:
        reddit.redditor(username).message(subject, message)
    except praw.exceptions.RedditAPIException as e:
        for subexception in e.items:
            if subexception.error_type == "RATELIMIT":
                error_str = str(subexception)
                print(error_str)

                if 'minute' in error_str:
                    delay = error_str.split('for ')[-1].split(' minute')[0]
                    delay = int(delay) * 60.0
                else:
                    delay = error_str.split('for ')[-1].split(' second')[0]
                    delay = int(delay)

                time.sleep(delay)
            elif subexception.error_type == 'INVALID_USER':
                return True

        return False
    except Exception as e:
        print(e)
        return False

    return True

def main():
    reddit = praw.Reddit("bot", user_agent=USER_AGENT)
    
    subject = input("Subject: ")

    in_f = open("message.txt", "r", encoding="utf-8")
    templ = in_f.read()
    in_f.close()

    in_f = open("users.txt", "r", encoding="utf-8")

    for username in in_f:
        username = username.strip()
        print(username)
        
        message = templ.replace("{{username}}", username)
        
        while True:
            if try_posting(reddit, username, subject, message):
                break
            
        print(reddit.auth.limits)

        if reddit.auth.limits['remaining'] == 0:
            timeout = reddit.auth.limits['reset_timestamp'] - time.time()
            print("Used up requests in current time window - sleeping for {} seconds".format(timeout))
            time.sleep(timeout)

    in_f.close()

if __name__ == "__main__":
    main()

```

We instantiate a `Reddit` object and ask the user to input DM subject via standard input.
Then we read a template of the message from m message.txt and usernames (one per line) from users.txt.
We replace `{{username}}` in a template with actual user name to personalise a message. I could have used jinja2 for this,
but this is just a simple experimental script that does not warrant bringing a full-powered templating engine into the
picture.

Now we try posting the message by calling `try_posting` function. This function returns a boolean value:

* True if posting succeeded or if target user is invalid (no need to retry)
* False if posting failed for some reason other than target user being invalid.

If all goes well, the API call in `try` block does not throw any exceptions and we can proceed to next user.
But it turns out that Reddit API has a hidden rate limit on sending direct messages. When we hit that rate limit, we
are getting an exception of class 
[`praw.exceptions.RedditAPIException`](https://praw.readthedocs.io/en/latest/code_overview/exceptions.html#praw.exceptions.RedditAPIException)
that will have one or more sub-exceptions available in list at `items` property. To detect rate limiting, we
iterate across this list and check if there's a subexception with `error_type` equal to `RATELIMIT` string.

When converted to string, it will read something like the following:

```
praw.exceptions.RedditAPIException: RATELIMIT: "Looks like you've been doing that a lot. Take a break for 3 minutes before trying again." on field 'ratelimit'
```

This gives us delay duration in minutes or seconds. We do a little bit of string processing to dig out the delay value and 
call `time.sleep()` with it before trying to post again.

If something is wrong with the target user we will get subexception with `error_type` being equal to `INVALID_USER`. We
make sure to skip this user and refrain from further attempts to message them.

In the `main()` function we also check `limits` dictionary in [`Auth`](https://praw.readthedocs.io/en/stable/code_overview/other/auth.html)
object that PRAW fills from the HTTP headers. This turned out to be unnecessary for our use case, as we have much tighter rate
limits for DM'ing people than the "official" Reddit rate limit of 30 requests per minute.

I managed to get this stuff working, but wasn't able to growth hack my way to wealth as Reddit suspended the account
for 3 days. However it does seem to work more or less fine on a sufficiently small scale, as long as the account is pre-warmed
and has some karma. API requests to send messages were instantly rejected on the freshly created account.


