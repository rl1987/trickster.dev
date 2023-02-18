+++
author = "rl1987"
title = "Understanding HTTP/2 fingerprinting"
date = "2023-02-28"
draft = true
tags = ["scraping", "automation"]
+++

Incoming HTTPS traffic can be fingerprinted by server-side systems to derive
technical characteristics of client hardware and software. One way to do this
is TLS fingerprinting that we have covered before on this blog and that
is commonly done by antibot vendors as part of automation countermeasures suite.
But that's not all they do. Fingerprinting can be done at HTTP/2 level as well.
Let us discuss how.


