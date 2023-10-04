+++
author = "rl1987"
title = "Setting up mitmproxy with iOS 17.1"
date = "2023-10-04"
draft = true
tags = ["automation", "security", "mitmproxy"]
+++

[mitmproxy](https://mitmproxy.org/) is open source, interactive proxy server
meant for interception, capture and analysis of network traffic for purposes such
as penetration testing, debugging, troubleshooting, reverse engineering and
privacy analysis. A common use case of this tool is to explore mobile application
network traffic (typically API calls over HTTPS) for API scraping, automation and
security testing purposes. Earlier in the blog I have covered how to set up 
mitmproxy with mobile device that run iOS 15. Today iOS 17.1 beta 2 is available
for testing and thus we will go through the process of setting it up with 
mitmproxy.

Let us start with installing mitmproxy itself. There are several ways to do
it depending on your need and specifics of dev environment:

* On macOS you can install it through Homebrew: `brew install mitmproxy`.
* If you want to develop mitmproxy extensions in Python it can be installed
via PIP: `pip3 install mitmproxy`. 
* If you want to run it via Docker, the [official image](https://hub.docker.com/r/mitmproxy/mitmproxy/)
is available on Docker hub.
* Some Linux distributions (e.g. Debian, Arch, Kali) ship mitmproxy in their
package managers.
* Windows installer, source tarballs and Linux/macOS binaries are available from 
the [official website](https://mitmproxy.org/).

To make sure you have it installed correctly, run it with `--version` CLI 
argument:

```
$ mitmproxy --version
Mitmproxy: 10.0.0
Python:    3.11.5
OpenSSL:   OpenSSL 3.1.3 19 Sep 2023
Platform:  macOS-13.5.2-arm64-arm-64bit
```

Now run the mitmproxy TUI program in terminal of your local machine. Doing this
on server is possible as well, but not recommended. Either way, you need to make
sure that your iPhone can reach the mitmproxy server via the network. A typical
setup is having them both in a single WiFi network.

Now you need to find out the IP address of your server:

* On macoS run `ifconfig` and look for IPv4 address under your primary network
interface (e.g. `en0`).
* On Linux it will depend on exact system specifics, but you can try using 
`ifconfig` if available, or running `ip addr` or `hostname -I`.
* On Windows it will be availabe in the output of `ipconfig` command.

If you have desktop GUI environment running the IP address will be available
through network setting app as well.

