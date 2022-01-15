+++
author = "rl1987"
title = "Clubhouse API scraping with Python and mitmproxy"
date = "2022-01-16"
draft = true
tags = ["python", "mitmproxy", "scraping"]
+++

In recent years, Clubhouse - a mobile app for audio-based social networking - has gained significant prominence
and somehow made people very excited about a fairly old concept of VoIP teleconferencing. Let us take a look into 
HTTP API calls this app is performing and see if we can extract some data.

The tool we will be using for intercepting HTTP traffic is called [mitmproxy](https://mitmproxy.org/). It is a little
HTTP proxy server that can be launched on your computer and provide a way to inspect and modify the HTTP traffic even
if TLS is used. Luckily Clubhouse app does not perform TLS cert pinning which makes it fairly easy to intercept 
private API calls with a proper setup.

I won't be covering how to set up mitmproxy with your mobile device as there are many blog posts and Youtube videos
detailing on how to do this with both iOS and Android devices. You may want to check out:

* [Intercept iOS/Android Network Calls using mitmproxy](https://medium.com/testvagrant/intercept-ios-android-network-calls-using-mitmproxy-4d3c94831f62) on Medium
* [Reverse Engineering a Private API with mitmproxy](https://www.youtube.com/watch?v=xQGC-8ojYbU) on Youtube



