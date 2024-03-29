+++
author = "rl1987"
title = "Tools of the trade for scraping and automation"
date = "2022-02-06"
tags = ["automation", "scraping"]
+++

To get things done, one needs a set of tools appropriate to the task. We will discuss several open source
tools that are highly valuable for developers working in scraping and automation.

Chrome DevTools
----------------

Let us start with the basics. Chrome has a [developer tool panel](https://developer.chrome.com/docs/devtools/) 
that you can open by right-clicking on something in the web page and choose "Inspect Element" or by going to 
View -> Developer -> Developer Tools. There are following tabs in the DevTools panel: 

* Elements - allows you to inspect and modify the DOM tree that exists *after* client-side rendering (to view the page source
*before* client side rendering, you may want to go to View -> Developer -> View Source). 
* Console - a client-side JS shell that prints JS warnings/errors and also lets you type in your own JavaScript to be executed in
the current page.
* Sources - provides you with an interface to read HTML, JavaScript and CSS source files that browser has downloaded when
rendering the page.
* Network - provides visibility into network communications originating from browser when page is being load and also when 
user actions are being performed. Very useful for reverse engineering.
* Performance - provides tooling to measure page performance in terms of where time is being spent in the browser.
* Memory - provides tooling to measure memory performance and also to inspect memory contents of JS environment of the current page.
* Application - provides access to client side data being stored in the browser. We may want to take cookies from here if it is
not feasible or desirable to implement automated code to go through steps to get them automatically.

Depending on the version of your Chrome instance and extensions you have installed, you may have more tabs in you DevTools.
As web scraper developer I am spending most time in Elements and Network tabs and barely use other ones.

In Network tab you can choose an HTTP request you want to reproduce programmatically, right-click on it and choose Copy ->
Copy as cURL. Which brings us to...

cURL
----

[cURL](https://curl.se/) is a command line program that is essentially a Swiss army knife of application-level networking. 
It supports a number of application level protocols, but mostly we are interested in HTTP(S). If you have a cURL snippet
copied from Network tab of Chrome DevTools, you can paste it into small shell script and do further experimentation.
For example, you can add `--verbose` option to make cURL print some protocol-level details about request-response flow you are
reproducing. If you want to go extra deep, try running it with `--trace-ascii -`: `curl https://www.trickster.dev --trace-ascii -`.
You may also want to remove some headers/cookies/parameters to see which parts of request are necessary for it to succeed.

cURL project also ships libcurl - a C library that has many wrappers in many programming languages. However it is fairly low-level
and not the best choice for a typical scraping or automation project.

curlconverter
-------------

But eventually we want to reproduce the requests in some actual programming language. This is where 
[curlconverter](https://curlconverter.com/) comes in. It's a small webapp that takes cURL commands and converts them into
snippets in one of several programming languages: Python, Dart, Golang, Rust and a few more. This makes it quick to go from
finding a key request-response flow in DevTools to reproducing it in your own code.

mitmproxy
---------

[mitmproxy](https://mitmproxy.org/) is a small proxy server that is used to tap into communications of networked software,
mostly HTTP-based API calls. This is similar to Network tab in DevTools, except that you are not limited to reverse engineering
requests your browser makes, but can also see what mobile apps are doing over the network. Furthermore, once you are doing
MITM attacks you can modify or replay requests of interest, which opens various possibilities for security work, such as looking
for security vulnerabilities or privacy leaks. mitmproxy also provides a [Python API](https://docs.mitmproxy.org/stable/addons-overview/)
for developing your own addons.

Using mitmproxy allows one to discover and tap into private APIs of mobile apps, which we have discussed earlier. However it is
required that X.509 certificate validation is not being enforced too strictly - if an app you want to hack is implementing
certificate pinning you will need to find a way to defeat it.

tmux
----

[tmux](https://github.com/tmux/tmux) is a terminal multiplexer program that provides a simple way to run long-running tasks
(e.g. massive scraping jobs or long-term automations) or remote Linux/Unix server. You would need to start a tmux session by
launching tmux with no CLI arguments, launch your stuff in the tmux session and press `Ctrl-b d` to detach it. Now it's safe
to close your SSH connection - your automation will keep running in a detached session. When you reconnect, launch 
`tmux attach` to attach to your last session. If you have multiple sessions running in the background, you may need to use
`-t` option with name or number of session you want to go back to, such as: `tmux attach -t 1`. Furthermore, tmux provides
more functionality, such as splitting terminal window into multiple subwindows (panes, tabs) and so forth.

I find it very cheap and convenient to run my long-running scripts inside tmux sessions on disposable $5/month virtual private
servers from Digital Ocean.

Crontab UI
----------

You or your customer may want to run automation at some fixed time-based schedule. One way to get it done is to configure
cronjobs on your Unix/Linux server of Kubernetes cluster. However, you may want to have web-based dashboard for managing
your cronjobs that is at least somewhat comprehensible to your not-so-technical customer who just wants to adjust the schedule
once in a while. This is where [Crontab UI](https://github.com/alseambusher/crontab-ui) comes in. It's a Node.js-based webapp
that provides a simple web interface for cronjob management. It can be installed through NPM and also has an
official [Docker image](https://hub.docker.com/r/alseambusher/crontab-ui).

n8n
---

Sometimes simply running some Unix commands at schedule will not be enough and more complex automation flow will be necessary.
[n8n](https://n8n.io/) is extendable workflow automation system that enables people to build automations with little to no
programming in some cases. Think of this as open-source equivalent of famous "no code" tools like Zapier and Integromat. However
I don't recommend that people buy into No Code hype too much as this sort of graphical workflows can turn into it's own kind of
spaghetti code once you reach some non-trivial complexity. However, this can be still useful when connecting various actions
(e.g. execution of scripts you coded yourself) into some greater automated workflow. Like Crontab UI, n8n can be installed 
via NPM or Docker.


Vagrant
-------

Dealing with differences in development environment can be pain. [Vagrant](https://www.vagrantup.com/) is a virtual machine
management program that enables you to have a consistent development environment based from a single source of truth (your
Vagrantfile, possibly with some provisioning scripts). It's essentially infrastructure-as-code, but for Virtualbox/VMWare 
virtual machines that can be created and destroyed on as-needed basis.

