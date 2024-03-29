+++
author = "rl1987"
title = "Back to the terminal: the new era of CLI and TUI software"
date = "2023-08-09"
tags = []
+++

With desktop GUI apps becoming generally becoming increasingly bloated and
sluggish over time (largely thanks to growing popularity of Electron.js) some
technical users are turning back to sofware using the simpler and leaner user 
interfaces - command line and pseudo-GUIs being rendered in ASCII/Unicode (text
user interfaces). CLI tools have the additional benefit of being relatively easy
to be used via subprocceses from automation scripts. We will take a look at 
some modern software that is meant be used via terminal. 

Carbonyl: 21st Century Lynx
---------------------------

Remember [Lynx](https://lynx.invisible-island.net/), a text-only web browser
to render web pages in simplified, text only form? Funny thing is, Lynx is still
being maintained to some degree, but lack of support for client-side JavaScript
largely makes it obsolete for browsing the modern web, even if we consider the
lack of image rendering to be a feature. 

[Carbonyl](https://github.com/fathyb/carbonyl) is a Chromium fork that is a
modern take on TUI-based web browser idea. If you have Docker installed you can
easily try it out:

```
$ docker run --rm -ti fathyb/carbonyl https://trickster.dev
```

[Screenshot 1](/2023-08-08_14.36.27.png)
[Screenshot 2](/2023-08-08_14.41.51.png)

It works quite well with simpler sites, but it can run into issues when you 
trip something up in anti-automation solutions. Another limitation is that you
cannot watch videos with sound.

ag, ripgrep - the new grep(1)
-----------------------------

You use grep(1) when you want to search something in source code or text file(s).
[The Silver Search](https://github.com/ggreer/the_silver_searcher) (`ag`) is 
a tool similar to grep, but designed to search for substrings in source code
and optimised for that end.

[Ripgrep](https://github.com/BurntSushi/ripgrep) is another grep-like tool to
run fast searches for text in a directory tree (with regex support), while 
also respecting your .gitignore file.

bottom, btop, glances - better kind of top(1)
---------------------------------------------

In Linux/Unix systems top(1) is a TUI tool that renders a list of running
processes with their resource consumption numbers - similar to Activity Monitor
in macOS or Task Manager in Windows. Many tech people are aware of 
[htop](https://htop.dev/) - an alternative tool with enhanced interactivity.

But we can go even further. [Bottom](https://github.com/ClementTsang/bottom) 
(`btm`) is a Rust program that renders resource consumption graphs in Unicode
pseudo-graphics with a process list.

[Screenshot 3](/2023-08-08_14.56.57.png)

[btop](https://github.com/aristocratos/btop) and 
[glances](https://github.com/nicolargo/glances) are another programs similar to 
Bottom. 

Terminal Image Viewer (tiv)
---------------------------

But what if you want to take a quick glance at pictures without having a GUI
environment? Perhaps you have some web scraping project that involves downloading
images and it's bit of pain to use scp(1) or sftp(1) to download them from 
the server in order to preview them. [Terminal Image Viewer](https://github.com/stefanhaustein/TerminalImageViewer)
is a C++ program that relies on features of modern terminals for actually
quite good image rendering.

[Screenshot 4](/2023-08-09_10.32.36.png)

Note however that this does not work on default Terminal app on macOS - you 
will need iTerm for this.

HTTPie - command line API client
--------------------------------

[HTTPie](https://httpie.io/) is a CLI tool designed specifically for launching 
requests against RESTful APIs. Unline curl, which is more general tool, HTTPie
provides a simple CLI that directly maps into aspects of HTTP requests you want
to generate:

```
$ http GET https://ifconfig.me/all.json
HTTP/1.1 200 OK
Alt-Svc: h3=":443"; ma=2592000,h3-29=":443"; ma=2592000
Via: 1.1 google
access-control-allow-origin: *
content-length: 268
content-type: application/json; charset=utf-8
date: Tue, 08 Aug 2023 12:17:07 GMT
server: istio-envoy
strict-transport-security: max-age=2592000; includeSubDomains
x-envoy-upstream-service-time: 1

{
    "encoding": "gzip, deflate, br",
    "forwarded": "[REDACTED], 34.160.111.145,35.191.2.1",
    "ip_addr": "[REDACTED]",
    "method": "GET",
    "mime": "*/*",
    "port": 60392,
    "remote_host": "unavailable",
    "user_agent": "HTTPie/3.2.2",
    "via": "1.1 google"
}


```

We can see it also pretty-prints the JSON payload in the response. 

jq - CLI tool and DSL for JSON processing
-----------------------------------------

If pretty-printing the JSON is not enough, you can use [jq](https://jqlang.github.io/jq/) -
a CLI tool that provides an entire Domain Specific Language for JSON wrangling.

tshark - CLI equivalent of Wireshark
------------------------------------

Wireshark is a prominent packet sniffer used by network engineers, security
people and software developers. [TShark](https://www.wireshark.org/docs/man-pages/tshark.html) 
is a relatively obscure sibling of Wireshark that is CLI-based. Think of it
as a tcpdump(1), but better. It can be used to not only capture network traffic,
but to run various filters and statistical techniques for traffic analysis
purposes.

TermShark
---------

But what if you want something like Wireshark GUI in your terminal environment?
[TermShark](https://termshark.io/) is a TUI wrapper for TShark that renders
a user interface similar to that of Wireshark.

[Screenshot 5](/2023-08-09_14.40.29.png)

mitmproxy
---------

When doing exploration of web and mobile apps for security research or 
automation one may want to intercept API traffic to see what conversations 
between the app and remote servers. [mitmproxy](https://mitmproxy.org/) is 
an interactive TUI program that works as HTTP(S) proxy server meant to capture 
and inspect the HTTP(S) requests. It's a simpler alternative to Burp Suite GUI
app that you can also customise with your own plugin code.

neovim
------

[Neovim](https://neovim.io/) is a modernised and more extensible addition to
the vi/VIM text editor lineage with features like Language Server Protocol
support, Lua scripting interface, improved usability, RPC API, system clipboard
integration, built-in terminal emulator and so on.

GitHub CLI tool
---------------

There's git(1), and there's GitHub. The former is CLI tool and the latter is
web-based platform. To bridge the gap between the two there's a Github
[CLI tool](https://cli.github.com/) for doing tasks like working with tickets,
managing pull requests and configuring the CI system. This can be helpful
when doing devops work to automate various aspects of software development
lifecycle.

mapscii
-------

But what if you want to see some maps in your terminal? You can do that with
[mapscii](https://github.com/rastapasta/mapscii) - a Node.JS program that
renders OpenStreetMap data in terminal environment with mouse support. If you
don't want to install it via NPM you can access a test instance via telnet 
protocol:

```
$ telnet mapscii.me  
```

[Screenshot 6](/2023-08-09_13.27.37.png)

Visidata
--------

In scraping and automation it is very common to deal with tabular data in formats
such as CSV files, Excel spreadsheets, SQLite databases and so on. 
[Visidata](https://www.visidata.org/) is TUI application for doing exactly that.
It does a good subset of what Excel can do - data filtering, rendering some 
charts (for example, Shift-F quickly renders a histogram of values in the current
column), lettting you edit cells and so on. 

[Screenshot 7](/2023-08-09_13.39.44.png)
[Screenshot 8](/2023-08-09_13.40.02.png)

Since Visidata is developed in Python you can install it via PIP. It is also 
available on packet managers of some Linux systems.

Radare2
-------

[Radare2](https://rada.re/n/) is a programmable binary reverse engineering 
toolkit for low-level hackers. Besides the main TUI program it also ships
`r2pipe` - a Python module for scripting binary analysis workflows (disassembly,
binary code analysis, runtime debugging).

Rich and Textual
----------------

These are all nice examples, but what if you want to develop something like
this yourself? Writing ncurses-based C programs is not the most productive
way to spend time in 2023. When it comes to Python CLI/TUI programming, there
are two inter-related projects of interest:

* [Rich](https://github.com/Textualize/rich) - a library for enhanced text
formatting.
* [Textual](https://github.com/Textualize/textual) - a TUI programming framework,
based on Rich (with CSS support).

To get a glimpse of what it can do, you can run:

```
$ python3 -m textual
```

[Screenshot 9](/2023-08-09_14.15.42.png)

