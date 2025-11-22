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

## Reverse proxy mode

In some cases you have a server that you want to spy on, or for some reason
setting up proxy configuration and X.509 cert is not viable for your use case.
To cover situations like this, mitmproxy allows you to run in reverse proxy mode.
Client would access mitmproxy as if it was a real server, but mitmproxy would
act as a spy in the middle between client and the server being "protected". This
is similar to a common use case of nginx server, except that it is being done
for the purpose of network interception.

## Transparent proxy mode

...

## mitmproxy as Wireguard VPN server

...

## SOCKS proxy mode

```
$ mitmproxy --mode socks5
```

This will launch mimtproxy as SOCKS5 server, bound to a standard port - 1080.
We can try it with curl:

```
$ curl --socks5 localhost --head https://nike.com -k -v
* Host localhost:1080 was resolved.
* IPv6: ::1
* IPv4: 127.0.0.1
*   Trying [::1]:1080...
* Host nike.com:443 was resolved.
* IPv6: (none)
* IPv4: 13.226.69.50, 13.226.69.57, 13.226.69.98, 13.226.69.103
* SOCKS5 connect to 13.226.69.50:443 (locally resolved)
* SOCKS5 request granted.
* Connected to localhost () port 1080
<...>
```

## mitmproxy as DNS server

...

## Passing traffic to upstream proxy

In some case, such as dealing with georestricted APIs, one may want to introduce
a second hop to some other proxy and pass the requests there. 

## mitmproxy virtual network interface

...

