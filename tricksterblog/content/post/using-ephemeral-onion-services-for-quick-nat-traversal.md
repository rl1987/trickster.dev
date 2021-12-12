+++
author = "rl1987"
title = "Using ephemeral Onion Services for quick NAT traversal"
date = "2021-12-15"
draft = true
tags = ["privacy", "devops"]
+++

Sometimes, when developing server-side software it is desirable to make it
accessible for access outside the local network, which might be shielded from
incoming TCP connections by a router that performs Network Address
Translation. One option to work around this is to use [Ngrok](https://ngrok.com/) - 
a SaaS app that lets you tunnel out a connection from your network and
exposes it to external traffic through a cloud endpoint. However, it is
primarily designed for web apps and it would be nice if we didn't need to rely
on a third-party SaaS vendor to make our server software accessible outside
our local network.

[Tor](https://www.torproject.org/) is an overlay network for anonymous
communications and censorship circumvention. The goal of Tor is to prevent the
gathering and analysis of traffic metadata (also known as traffic analysis). 
A detailed explanation of how Tor works
is outside the scope of this text, but the key principle is that hiding of routing
information is achieved by creating tunnel connection through 3 (or more, if
both parties are within Tor network) intermediate servers with telescoping
encryption layers - 3 layers of encryption to the first node, 2 layers of encryption
to middle node and 1 layer towards the exit node. The exit node removes the final layer
of encryption and works as a proxy server towards the ultimate destination of TCP
connection. Thus no single server is aware of both initiator and destination of
TCP connection.

Through a Tor feature called Onion Services, hiding a server is possible as well.
Turns out, setting up an Onion Service gives us NAT traversal for free, provided
that people accessing our server are okay to do it through Tor. 

[Tor daemon](https://gitlab.torproject.org/tpo/core/tor) is a piece of software that
implements all parts of the Tor network. For configuration during runtime, it can expose
a control port that we can connect to via TCP transport and run various requests
against a running Tor instance. [Tor Control Protocol](https://gitweb.torproject.org/torspec.git/tree/control-spec.txt)
is a relatively simple text-based network protocol that defines requests and responses
that Tor controllers (i.e. programs interacting with Tor instance via control port)
must be able to parse and generate. One of the commands it defines is `ADD_ONION`
at [Section 3.27](https://gitweb.torproject.org/torspec.git/tree/control-spec.txt#n1748)
that enables quick creation of Onion Services. We can provide cryptographic keys to be
used for this, but primarily we are concerned with port mapping between the local port
that our server is bound to (it's fine if it's binding the listener socket to the local host
address) and the port that Onion Service will be exposing. These can be either equal or
different, but it is an important detail to get right. Furthermore, ephemeral Onion
Services are bound to the lifecycle of control port connection - no need to worry about
removing them.

We could be doing a little socket programming, but we don't have to, as the Tor project
is also developing [Stem](https://stem.torproject.org/) - a Python module that implements
a Tor Control Protocol and enables us to quickly launch an ephemeral Onion Service.

I wrote the following quick script that connects to a local Tor instance 
(it could be a Tor browser bundle running locally) through the control port,
creates ephemeral Onion Service, uses its address to build this very blog through
[Hugo](https://gohugo.io/), and runs a local web server (`http.server` from vanilla Python
installation) on local port 8080.

```python
#!/usr/bin/python3

from stem.control import Controller

import http.server
import os
import subprocess
import sys

def main():
    controller = Controller.from_port()
    controller.authenticate()
    response = controller.create_ephemeral_hidden_service({80: 8080}, await_publication=True)

    assert(len(response.service_id) > 0)

    onion_url = "http://" + response.service_id + ".onion"
    print(onion_url, file=sys.stderr)

    os.chdir("tricksterblog/")

    subprocess.run(["hugo", "--baseURL", onion_url])

    os.chdir("public/")

    subprocess.run(["python3", "-m", "http.server", "8080"])


if __name__ == "__main__":
    main()

```

To encapsulate everything within a reproducible environment, the following Docker configuration
could be used:

```dockerfile
FROM debian:11

RUN apt-get update && apt-get install -y python3 python3-pip hugo tor
RUN pip3 install stem

ADD . /trickster.dev
WORKDIR /trickster.dev

ENTRYPOINT bash -c "tor --RunAsDaemon 1 --ControlPort 9051 && python3 run_onion_service.py"

```

Admittedly there are some opportunities for optimization here, as the size of resulting Docker
image is over 700 MB. However the code in this post is meant to be only a demonstration for
using Tor to expose a server in a NATted network.

[Screenshot](/2021-12-12_14.27.47.png)

Lastly, I would not recommend doing this in corporate networks, as your IT department and 
security people might disapprove. Not only this solution can be considered to be Shadow IT, but
using Tor in the corporate environment might raise suspicions of data exfiltration. Proceed with
caution.

