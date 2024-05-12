+++
author = "rl1987"
title = "Simple ways to find exposed sensitive information"
date = "2024-05-31"
draft = true
tags = ["scraping", "osint", "security"]
+++

Informational advantage is a form of power. On the flipside, exposure of sensitive
information about a person or organisation can be a privacy/security problem.
Sensitive Data Exposure is a type of vulnerability where software system (or 
user) makes sensitive data (API keys, user information, private documents, etc.) 
available to potential adversaries. For example, web app that lets users edit 
potentially confidential documents may be storing them in S3 buckets without
any proper access controls. This results in information that should not be
public being potentially available to those who know how to look for it. In this
post we will go through some basic techniques of Sensitive Data Discovery - 
the activity of hunting for accidental leaks of things that are best kept hidden.

One way to look for potentially sensitive information is to do search engine 
dorking - launching queries specifically crafted to narrow down on specific, 
potentially sensitive things. 

For example, the following query (Google dork) would look for PDF documents 
containing the word "confidential" and hosted under specific domain:

```
filetype:pdf site:hackerone.com "confidential"
```

We have used [`filetype:`](https://developers.google.com/search/docs/crawling-indexing/indexable-file-types#search-by-file-type)
operator to limit result to specific file extension and 
[`site:`](https://developers.google.com/search/docs/monitor-debug/search-operators/all-search-site)
operator to limit them to specific domain.

Of course, not every document containing word "confidential" is actually 
confidential, but a query like this could be a starting point to check if 
nothing sensitive is being leaked.

Another, more realistic example is the following Google query:

```
"contractors" filetype:xls "@gmail.com" site:gov
```

Automating Google dorking can be done via many of SERP scraper APIs available, 
but at the end of the day you will need to review the results manually.

On the very first page of search results I was able to find actual lists of 
government agency (e.g. Illinois Dept. of Transportation) contractors with email
addresses. Since pretending to be a contractor is very viable social engineering
vector that can lead to unauthorised access (physical and/or digital) to the 
sensitive infrastucture this sort of information exposure can have pretty serious
security implications. Furthermore, service-based businesses should take care 
not to expose their lead list spreadsheet on the public web as they can
potentially be found by some growth hacker working for the competition.

Another way to look for more technical sensitive data exposures is to search on
Github. 

For example, the following query (Github dork) looks for instances of Git 
credentials file being accidentally commited to public repos:

```
path:**/.git-credentials
```

We can also look for API keys to paid or private services. Github search query
can be derived from sample code related to the API. Let me give you a real
example. Google maps iOS SDK sample code repo contains the follow code
in [MapsAndPlacesDemo/MapsAndPlacesDemo/ApiKeys.swift](https://github.com/googlemaps-samples/maps-sdk-for-ios-samples/blob/main/MapsAndPlacesDemo/MapsAndPlacesDemo/ApiKeys.swift)
file: 

```swift
/// API keys needed for this project
public enum ApiKeys {
    #error("Register for API keys and enter them below; then, delete this line")
    static let mapsAPI = ""
    static let placesAPI = ""
}
```

Now there is a chance that some people trying out the GMaps iOS SDK filled in
the API keys and commited the code to public repository. Indeed, the following
Github dork gives us what seem to be some real API keys to Places API:

```
"static let placesAPI"
```

However, it must be noted that Github has [secret scanning automation](https://docs.github.com/en/code-security/secret-scanning/about-secret-scanning)
running to warn users about accidentally publishing API keys for a growing list
of partner services (and revoke leaked ones), which makes this trick less 
viable as time goes on. 

But what if we want to find API keys and other sensitive pieces of information
on websites running in production? In this case [PublicWWW](https://publicwww.com/) - 
a code-level search engine - can be helpful. To look for some API keys hardcoded
into client-side JS snippets we can run queries like:

```
"api_key" depth:all
"apiKey" depth:all
```

Again, not everything you will find like this is going to be sensitive data.
Some API keys are not meant to be kept secret.

Like with Google, we can use `site:` operator to limit the results to given 
domain. However, PublicWWW results are limited to users without paid account
and one must pay up to get the full results. Paying users can also search for
stuff via API.

WRITEME: open S3 buckets

WRITEME: people not keeping their mouths shut on social media
