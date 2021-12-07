+++
author = "rl1987"
title = "Using ephemeral onion services for quick NAT traversal"
date = "2021-12-15"
draft = true
tags = ["privacy", "devops"]
+++

Sometimes, when developing server-side software it is desirable to make it
accessible for access outside the local network, that might be shielded from
incoming TCP connections by a router that performs Network Address
Translation. One option to work around this is to use [Ngrok](https://ngrok.com/) - 
a SaaS app that let's you tunnel out a connection from your network and
exposes it to external traffic through a cloud endpoint. However it is
primarily designed for web apps and it would be nice if didn't need to rely
on a third party SaaS vendor to make our server software accessible outside
our local network.

[Tor](https://www.torproject.org/) is an overlay network for anonymous
communications and censorship circumvention. 

WRITEME: explain Tor and Onion Services

