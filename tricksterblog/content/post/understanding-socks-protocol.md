+++
author = "rl1987"
title = "Understanding SOCKS protocol"
date = "2024-04-30"
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

There are two major versions of SOCKS protocol: legacy SOCKS4A and slightly newer,
more advanced SOCKS5. Since SOCKS5 has some proper RFCs published to be used
as specifications it will be our primary focus. At macro level, primary purpose
of SOCKS5 protocol is to let user connect to a proxy server and provide a way to
"outsource" a secondary connection originating from proxy server and terminated
at the true destination the user wants to connect to. The original purpose for
this was enabling network firewalls to provide a controlled access to servers
running within private network.

