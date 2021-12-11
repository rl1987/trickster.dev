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

WRITEME: explain Tor Control protocol and command to create ephemeral HS

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

```dockerfile
FROM debian:11

RUN apt-get update && apt-get install -y python3 python3-pip hugo tor
RUN pip3 install stem

ADD . /trickster.dev
WORKDIR /trickster.dev

ENTRYPOINT bash -c "tor --RunAsDaemon 1 --ControlPort 9051 && python3 run_onion_service.py"

```

WRITEME: wrap things up and warn against doing this in corporate networks.

