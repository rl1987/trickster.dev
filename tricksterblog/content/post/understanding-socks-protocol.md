+++
author = "rl1987"
title = "Understanding SOCKS protocol"
date = "2024-04-25"
tags = ["networking"]
draft = true
+++

In computer networking a proxy server is intermediate party (software that may or
may not be running on a separate server) to transfer application-level traffic
between client and the another server. There are two major ways this can be
accomplished: message forwarding (largely limited to plaintext HTTP) and 
connection tunneling. SOCKS is a widely utilised protocol that implements
the latter approach. Proxy servers may be useful for caching, load balancing, 
network traffic inspection, hiding real traffic source from target servers, 
bypassing censorship/geo-blocking and filtering the traffic. Today we will look
how SOCKS protocol works to relay the traffic between client and target server.


