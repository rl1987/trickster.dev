+++
author = "rl1987"
title = "Email harvesting from Github profiles"
date = "2022-02-19"
tags = ["python", "growth-hacking"]
+++

You may have some reason to automatically gather (harvest) software developer emails. That might be SaaS marketing
objectives, recruitment or community building. One place online that has a lot of developers is Github. Some
of the developers have a public email address listed on their Github profile. Turns out, this information is available
through Github's [REST API](https://docs.github.com/en/rest) and can be extracted with just a bit of scripting.

First we need an API token. Log in to your Github account and go to [Personal Access Tokens](https://github.com/settings/tokens)
page. Press "Generate new token" button - Github will ask for your password. Now type in some name, choose expiration date (or
no expiration) and tick the following checkboxes under "Select scopes":

* `public_repo`
* `user:email`

Press "Generate token" button on the bottom of the page. Now it gives you an API token to be used in the code without going through
the OAuth flow. Make sure to copy it somewhere, as this token will not be shown again. We will be setting `Authorization` header
with this token when making API calls.

Our API scraping strategy will be as follows:

1. Scrape `/search/repositories` API for repos matching language and query (we can use `language:` operator to get repositories
developed in a specific programming language). We extract repo name, description, web URL and contributors URL. These fields are saved
into CSV file that next script will read. 

2. The second script reads repo CSV file and iterates across contributor URLs to get a list of contributors for each repository.
In the inner loop, it iterates across contributors, fetches their profiles from API, which gives us their emails. Names, usernames,
account creation dates and email addresses are saved into CSV file.

For API documentation, see: 

* https://docs.github.com/en/rest/reference/search#search-repositories
* https://docs.github.com/en/rest/reference/repos#list-repository-contributors
* https://docs.github.com/en/rest/reference/users#get-a-user

The first script that scrapes API for matching repos is as follows:

```python
#!/usr/bin/python3

import csv
import configparser
from pprint import pprint
import time

import requests

FIELDNAMES = [ "name", "description", "html_url", "contributors_url" ]

def create_session():
    session = requests.Session()

    config = configparser.ConfigParser()
    config.read('harvest.ini')

    token = config['GH']['Token']

    session.headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': 'token ' + token,
        'User-Agent': 'GithubEmailHarvest',
    }

    return session

def main():
    language = input("Language [Python]: ")
    query = input("Query: ")

    if language == "":
        language = "Python"
    
    session = create_session()

    page = 1
    
    q = '{} language:{}'.format(query, language)

    out_f = open("repos.csv", "w+", encoding="utf-8")
    
    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()

    while True:
        params = {
            'q': q,
            'page' : str(page),
        }

        resp = session.get('https://api.github.com/search/repositories', params=params)
        print(resp.url)
        print(resp.headers)

        json_dict = resp.json()

        items = json_dict.get('items')
        if items is None or len(items) == 0:
            pprint(json_dict)
            break

        for item_dict in items:
            row = {
                "name" : item_dict.get("name"),
                "description" : item_dict.get("description"),
                "html_url" : item_dict.get("html_url"),
                "contributors_url" : item_dict.get("contributors_url"),
            }

            pprint(row)

            csv_writer.writerow(row)
        
        page += 1
        
        time.sleep(1.2)

    out_f.close()

if __name__ == "__main__":
    main()
```

The second script that reads repository CSV file and scrapes developer names/emails is as follows:

```python
#!/usr/bin/python3

import csv
import time
from pprint import pprint

import requests

from search_repos import create_session

FIELDNAMES = [ "name", "login", "email", "joined_at" ]

def main():
    in_f = open("repos.csv", "r")

    out_f = open("contacts.csv", "w", encoding="utf-8")
    
    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()

    csv_reader = csv.DictReader(in_f)
    next(csv_reader)

    session = create_session()

    for in_row in csv_reader:
        url = in_row.get('contributors_url')

        resp = session.get(url)
        print(resp.url)

        json_arr = resp.json()
    
        for contrib_dict in json_arr:
            url = contrib_dict.get('url')

            resp = session.get(url)
            print(resp.url)

            json_dict = resp.json()

            if json_dict.get('email') is None:
                continue

            row = {
                'name' : json_dict.get('name'),
                'login' : json_dict.get('login'),
                'email': json_dict.get('email'),
                'joined_at' : json_dict.get('created_at'),
            }

            pprint(row)

            csv_writer.writerow(row)

            time.sleep(1)

        time.sleep(1)

if __name__ == "__main__":
    main()
```

Note that Github API does some rate limiting, especially when it comes to search requests. This is why
there are some delays made with `time.sleep()` in the code.

What if you don't want your Github account email publically available and harvestable? There is a simple
way to hide it: go to [Emails](https://github.com/settings/emails) page of your account settings
and make sure that "Keep my email addresses private" checkbox is ticked.
