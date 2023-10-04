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
communications (typically API calls over HTTPS) for API scraping, automation and
security testing purposes. Earlier in the blog I have covered how to set up 
mitmproxy with mobile device that run iOS 15. Today iOS 17.1 beta 2 is available
for testing and thus we will go through the process of setting it up with 
mitmproxy.

Let us start with installing mitmproxy itself. There are several ways to do
it depending on your needs and specifics of dev environment:

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

Now run the mitmproxy TUI program in terminal of your local machine (behind NAT). 
Doing this on server is possible as well, but not recommended. Either way, you 
need to make sure that your iPhone can reach the mitmproxy server via the network.
A typical setup is having them both in a single WiFi network.

Now you need to find out the IP address of your server:

* On macoS run `ifconfig` and look for IPv4 address under your primary network
interface (e.g. `en0`).
* On Linux it will depend on exact system specifics, but you can try using 
`ifconfig` if available, or running `ip addr` or `hostname -I`.
* On Windows it will be available in the output of `ipconfig` command.

If you have desktop GUI environment running the IP address will be available
through network setting app as well.

Let us do the setup on iPhone side. Make sure you are connected to the right
network and go to the Settings app. Press Wi-Fi cell in the table view and tap
the `(i)` button next to the name of Wi-Fi network you are connected to. In the
next screen go to the bottom of the table and tap "Configure Proxy" cell. 

Choose "Manual" from the available options and fill the little form here:

* In "Server" cell enter the IP address of your computer you have determined 
earlier.
* In "Port" field enter proxy port number - 8080.

Press the "Save" button on the top of UI. 

To intercept the HTTPS traffic, we need to install an X.509 certificate. Open the
Safari (specifically Safari - not some other browser) and navigate to mitm.it.
Press the green button under "iOS" heading. Allow the browser to download the
file into your system.

Install the certificate through Settings app: go to General, then to "VPN &
Device Management". You will find "mitmproxy" entry under "Downloaded Profile"
label. Tap it and press Install button in the modal view. Since this is a 
sensitive action, iOS will ask for PIN code and additional verification. If all
goes well, a "Verified" label with a checkmark will appear on the GUI.

But this is not enough. We installed the certificate, but we also need to trust
it. Go back to General section of settings, then go to About and choose
"Certificate Trust Settings" at the bottom. Turn on the switch for the 
mitmproxy certificate. 

Now let us verify that it works correctly. Go back to Safari and open some 
website that is protected by TLS (which most modern websites do). You should
see HTTPS requests related to the site displayed in mitmproxy TUI.

If this does not work right away you may want to set your iPhone to airplane
mode for a brief period of time and make it reconnect to Wi-Fi network. That
used to help in earlier versions of iOS.

If you don't like the TUI version of mitmproxy you can try mitmweb. It also ships
with mitmproxy, but presents data in web interface.

Another thing that ships with mitmproxy is mitmdump - a tool similar to
tcpdump, but based on mitmproxy machinery and made to primarily intercept
HTTP(S) traffic:

```
$ mitmdump
[13:29:03.684] HTTP(S) proxy listening at *:8080.
[13:29:04.825][192.168.0.16:52306] client connect
[13:29:04.883][192.168.0.16:52306] server connect bam.nr-data.net:443 (162.247.243.29:443)
192.168.0.16:52306: POST https://bam.nr-data.net/jserrors/1/NRBR-26d48a12bc762b8fbd7?a=45012625&v=1.242.0&to=ZVdXbUtXXBIHVUNfXlwde1ZLW1MND0xSUmRAWxoT&rst=93147&ck=0&s=25398efdfbe5dc5f&ref=https://www.nike…
                 << 200 OK 24b
[13:29:05.237][192.168.0.16:52307] client connect
[13:29:05.298][192.168.0.16:52307] server connect www.nike.com:443 (2.18.32.173:443)
192.168.0.16:52307: POST https://www.nike.com/Fj-Dfn/Fyj/7WK/PLInpt0t/7pEchtzQph7ruY/STdCAQ/SVJ3bWdc/bUgB HTTP/2.0
        << HTTP/2.0 201 Created 18b
192.168.0.16:52307: POST https://www.nike.com/Fj-Dfn/Fyj/7WK/PLInpt0t/7pEchtzQph7ruY/STdCAQ/SVJ3bWdc/bUgB HTTP/2.0
        << HTTP/2.0 201 Created 18b
192.168.0.16:52307: POST https://www.nike.com/Fj-Dfn/Fyj/7WK/PLInpt0t/7pEchtzQph7ruY/STdCAQ/SVJ3bWdc/bUgB HTTP/2.0
 << stream reset by client (CANCEL)
192.168.0.16:52307: GET https://www.nike.com/w/air-force-1-shoes-5sj3yzy7ok HTTP/2.0
        << HTTP/2.0 200 OK 115k
[13:29:06.554][192.168.0.16:52308] client connect
[13:29:06.556][192.168.0.16:52309] client connect
...
```

When you no longer want the traffic to be intercepted, go back to "Configure
Proxy" table in iPhone settings and disable the proxying there.

[TODO: add screenshots]
