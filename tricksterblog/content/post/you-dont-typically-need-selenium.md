+++
author = "rl1987"
title = "You don't typically need Selenium for scraping and automation"
date = "2022-01-19"
draft = true
tags = ["python", "automation"]
+++

First, let us presume that we want to develop code to extract structured information from web pages that
may or may not be doing a lot of API calls from client side JavaScript. We are not trying to develop a
general crawler like Googlebot. We don't mind writing some code that would be specific for each site we
are scraping (e.g. some Scrapy spiders or Python scripts).

When coming across discussions about web scraper development on various forums online, it is common to hear
people saying that they need JavaScript rendering to scrape websites. Most commonly this is achieved by using
something like [Selenium](https://www.selenium.dev) - a technology to programmatically control a web browser. 
However, introducing Selenium into your web scraping systems brings the following problems:

* Performance penalty due to having to run an entire browser that downloads all website assets even if you don't
need them. This also has scalability implications for your web scraping activities.
* Stability issues due to race conditions between your code and client-side JavaScript code that runs in the 
browser. Developers who have used Selenium are painfully familiar with `WebDriverException`, 
`StaleElementReferenceException` errors, timeouts and difficulties getting simulated user events working reliably.
* Blocking evasion difficulties. Since you are running an entire web browser in a way regular user would
not (possibly in a headless mode) there are many ways that automation is being performed. For example,
the site could check `window.navigator.webdriver` boolean value and so on. To some extent, this can
be mitigated by [patching the web driver binary](https://stackoverflow.com/questions/33225947/can-a-website-detect-when-you-are-using-selenium-with-chromedriver/41220267)
or using projects like [undetected-chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver)
and [selenium-stealth](https://github.com/diprajpatra/selenium-stealth).

How can one ditch Selenium and avoid these problems? For almost all sites, the answer is rather simple.
You open the DevTools and do a little bit of reverse engineering, besides viewing web page source before
it gets processed by client-side JS code. When you click a link or button on the page, what requests are 
seen in the Network tab? Is it plain old HTTP GET request that simply fetches the next page? Is it some
nasty form submission via HTTP POST request that legacy ASP.NET sites tend to implement? Is it REST API
request that fetches new data so that it could be rendered on existing DOM? Is it GraphQL request?
Perhaps there is more complex API flow consisting of more back-and-forth between client and server?
If there is CSRF token somewhere in request, where does the browser take it from? Is there hidden
`<input>` with that token or is it hardcoded somewhere in JS snippet in the page? If specific cookies
are necessary for API calls to succeed, look earlier in the communication history to see where they
come from. If you submit a login form, what does the server return to the browser? Is it some HTTP
session cookie or API authorization token?

To experiment with reproducing the request for scraping and automation purposes, it is highly useful
to use "Copy as curl" feature in Network tab of DevTools. This copies a curl(1) command that you can
paste into small shell script or into tool like [curlconverter](https://curlconverter.com) to convert
it to code snippet. Next, you may want to experiment with removing various cookies, headers and parameters
to establish which components of request are necessary to have it successfully handled by the server.
Do this kind of analysis and experimentation across the entire flow you are interested and you will
be able to reproduce it in you own code without involving JS execution. 

Does this take some time and effort? Well, of course it does. However, tediously fighting crash bugs
in your Selenium-based code that result from race conditions also takes time and effort. I would
argue that it is more worthwhile to spend some time and effort reverse engineering the site even
if it is heavily based on client side JS rendering, as you gain performance and stability in the
code that you write. Furthermore, you may even save some time by being able to shift from scraping
HTML pages to scraping private APIs that provide JSON responses with pre-structured data that you
can conveniently parse without having to come up with multiple XPath queries or CSS selectors.

You may say that modern websites may have complex API flows that makes reverse engineering
difficult. Typically that is not the case. Most of the time you don't even need to do much
reading of JS code that does the client side rendering, as inspecting DOM tree and request-response
flows is sufficient. Remember: client side JS code is written by frontend developers who have
to manage complexity on their side. If they are making it overly complex for you, they are likely
shooting themselves in the foot as well.

Primary exception to this is when site is deliberately engineered to make it difficult to automate against.
This is mostly applicable to big social media portals that are proactively fighting scraping and
automation. Another example is Amazon login page (tinker with it with NoScript being off).
However, in that case they likely have countermeasures against Selenium as well.

Do I think that Selenium has no place in the toolkit of developer working on scrapers and automation?
No, I would not say that. In my opinion, the applicability of Selenium is for the following two cases:

1. Development of generalised code that crawls many sites and is not meant to be optimised
for any of them. An example of this could be a script that takes a list of URLs and tries to harvest
email addresses or other contact information.
2. As a fallback/plan B for sites that are very difficult to reverse engineer (e.g. Google Maps, 
some legacy ASP.NET web apps).

These two cases aside, I encourage everyone working on scraping and automation to take a slightly
deeper look into the inner workings of websites you are automating against. This will prove to be
worth your while.

Lastly, if you really need client-side rendering, you may want to try [Splash](https://www.zyte.com/splash/) -
an open source program from creators of Scrapy framework that is specifically developed for
web scraping purposes, whereas Selenium was originally designed for automated testing.

