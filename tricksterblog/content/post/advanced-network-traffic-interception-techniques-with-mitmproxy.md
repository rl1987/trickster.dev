+++
author = "rl1987"
title = "Advanced network traffic interception techniques with mitmproxy"
date = "2025-11-30"
draft = true
tags = ["security", "mitmproxy"]
+++

The most common way to use mitmproxy for API traffic interception is to use it
in a default forward proxy mode. One would run mitmproxy server on a laptop or
desktop computer, then configure proxy settings and install X.509 certificate
on a client device (e.g. smart phone). But there is more to mitmproxy than that.
It can also be used as reverse proxy, transparent proxy (on Linux and macOS),
Wireguard VPN server that also intercepts network traffic, SOCKS proxy server,
programmable DNS server and even as a virtual network interface on Linux. In 
this article we will go through some of the lesser known mitmproxy features
for uncovering what goes on between servers and clients.



