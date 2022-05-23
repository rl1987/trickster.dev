+++
author = "rl1987"
title = "Scraping Instagram API with Instauto"
date = "2022-05-31"
draft = true
tags = ["scraping", "python", "automation"]
+++

Instagram scraping is of interest to OSINT and growth hacking communities, but can be
rather challenging. If we proceed with using browser automation for this purpose we
risk triggering client-side countermeasures. Using private API is a safer, more performant
approach, but has it's own challenges. Instagram implements complex API flows that involve
HMACs and other cryptographic techniques for extra security. When it comes to implementing 
Instagram scraping code, one does not simply use mitmproxy or Chrome DevTools to intercept
API requests so that we could reproduce them programmatically. Significantly deeper reverse
engineering is needed: we would either try to make sense of the obfuscated frontend
JS code or decompiling/disassembling mobile app binaries to understand how exactly API
flows are implemented. Both of these approaches are labour intensive and require some fairly
deep, specialised knowledge.

Luckily for us, there's something called [Instauto](https://instauto.readthedocs.io/en/latest/index.html).
Instauto is a Python module that implements an unofficial client library for private Instagram
API. It saves us a mountain of work that we would have to do if we wanted to tap into
private Instagram API for gray hat use cases.

There are three major parts of Instauto:

* `instauto.api` - low level API client that we can use directly and that is used by rest of
the Instauto codebase.
* `instauto.helpers` - higher level API client that defines object-oriented API over raw Python
dictionaries/lists that it gets from `instauto.api`.
* `instauto.bot` - high-level utility code for Instagram botting. It builds upon `instauto.helpers`.

Before we proceed with programming, we need to create or buy a scraper account that is meant
to be disposable. Running any kind of gray hat activities on an account that has any kind of value
is asking for trouble, as Instagram is known to crack down on accounts involved in sketchy, robotic
activities. 

The following example will entail scraping list of followers given the username of some target
account, including email addresses that are sometimes available through API, but are not necessarily
visible on Instagram profiles.

We need to instantiate API client first and perform login step with username and password:

```python
from instauto.api.client import ApiClient

client = ApiClient(username=username, password=password)
client.log_in()
```

At this point Instagram might ask for access confirmation code that Instauto will let you
enter via standard input.

We want to avoid performing login step repeatedly, as this can trigger automation countermeasures.
To help us here, Instauto API client implements `save_to_disk()` method that we can call with
a filepath:

```python
client.save_to_disk("savefile.instauto")
```

This will create a JSON file with session data to be reused next time. To read this file
we will need to instantiate `ApiClient` as follows:

```python
client = ApiClient.initiate_from_file("savefile.instauto")
```

Assuming we have username of target account (without leading `@` character) we can use
`get_user_id_from_username()` from `instauto.helpers` to get the numeric user ID that we will
need for further steps:

```python
from instauto.helpers.search import get_user_id_from_username
user_id = get_user_id_from_username(client, target_username)
```

At this point we could use `get_followers()` from `instauto.helpers`, but let's proceed with
a slightly harder way to see how using stuff from `instauto.api` looks like. To get the
list of followers, we need to instantiate a request object and use it on API client:

```python
import instauto.api.actions.structs.friendships as fs

obj = fs.GetFollowers(user_id)
obj, response = client.followers_get(obj)
followers = response.json()["users"]
```

Instauto takes care of API pagination for us, but we would need to call `followers_get()`
repeatedly until we either collected a required number of entries or ran out of data to scrape
(make sure to use the updated request object).  At this point we have a fairly sparse data 
that does not include much beyond user names and IDs of the followers.

To get more fields, we need to request for profile info based on user ID of each follower:

```python
import instauto.api.actions.structs.profile as pr

obj = pr.Info(user_id)
fi = client.profile_info(obj)
```

The complete Python script that demonstrates follower info scraping is as follows:

```python
#!/usr/bin/python3

import csv
import sys
import os
from pprint import pprint

import instauto.api.actions.structs.friendships as fs
from instauto.api.client import ApiClient
from instauto.helpers.friendships import get_followers
from instauto.helpers.search import get_user_id_from_username
import instauto.api.actions.structs.profile as pr


def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("{} <target_username>".format(sys.argv[0]))
        return

    target_username = sys.argv[1]
    target_username = target_username.replace("@", "")

    if os.path.isfile("savefile.instauto"):
        client = ApiClient.initiate_from_file("savefile.instauto")
    else:
        username = input("Username: ")
        password = input("Password: ")
        client = ApiClient(username=username, password=password)
        client.log_in()
        client.save_to_disk("savefile.instauto")

    print(client)

    user_id = get_user_id_from_username(client, target_username)

    # followers = get_followers(client, user_id, 100)
    # print(followers)

    # Based on:
    # https://github.com/stanvanrooy/instauto/blob/master/examples/api/friendships/get_followers.py
    obj = fs.GetFollowers(user_id)

    obj, response = client.followers_get(obj)

    followers = response.json()["users"]
    print("Got {} followers".format(len(followers)))

    while True:
        obj, response = client.followers_get(obj)
        if not response:
            break

        new_followers = response.json()["users"]
        print("Got {} followers".format(len(new_followers)))
        followers.extend(new_followers)

    if len(followers) == 0:
        return

    out_f = open("followers.csv", "w", encoding="utf-8")

    csv_writer = csv.DictWriter(
        out_f, fieldnames=list(followers[0].keys()), lineterminator="\n"
    )
    csv_writer.writeheader()

    for f in followers:
        pprint(f)
        if f.get("linked_fb_info") is not None:
            del f["linked_fb_info"]
        csv_writer.writerow(f)

    out_f.close()

    out_f = open("follower_infos.csv", "w", encoding="utf-8")

    csv_writer = csv.DictWriter(
        out_f,
        fieldnames=[
            "username",
            "pk",
            "biography",
            "public_email",
            "public_phone_number",
        ],
        lineterminator="\n",
    )
    csv_writer.writeheader()

    for f in followers:
        print("Getting profile details for {}...".format(f.get("username")))
        user_id = f.get("pk")
        obj = pr.Info(user_id)
        fi = client.profile_info(obj)

        if type(fi) == dict:
            csv_writer.writerow(
                {
                    "username": fi.get("username"),
                    "pk": fi.get("pk"),
                    "biography": fi.get("biography"),
                    "public_email": fi.get("public_email"),
                    "public_phone_number": fi.get("public_phone_number"),
                }
            )

    out_f.close()


if __name__ == "__main__":
    main()
```

You may want to use proxy with this script. Since Instauto uses the well-known requests
module for making HTTP requests, it heeds `HTTPS_PROXY` environment variable. That's an 
easy way to tunnel traffic through proxy. 
