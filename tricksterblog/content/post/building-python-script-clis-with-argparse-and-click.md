+++
author = "rl1987"
title = "Building Python script CLIs with argparse and Click"
date = "2022-08-31"
draft = true
tags = ["python"]
+++

To make Python script parametrisable with some input data we need to develop
a Command Line Interface. This will enable the end user to run the script with
various inputs and provide a way to choose optional behaviors that the script
supports. For example, running the script with `--silent` suppresses the output
that it would otherwise print to the terminal, whereas `--verbose` makes the
output extra detailed with fine-grained technical details included. Scripts
with well developed CLIs can be invoked in a reproducible way and thus it is 
possible to integrate them into larger automation flows.

The simplest way to make Python script accept input from command line is to 
read the `sys.argv` list that is populated as the script is launched. Like in
C programs, `sys.argv[0]` is name of the program being launched, 
`sys.argv[1]` is the first argument, `sys.argv[2]` is the second one and so on.
Length of `sys.argv` list is number of argument plus one - if there's no CLI
arguments being passed into the script it will be 1.

The following trivial script exemplifies how this can be used to implement 
a very basic CLI:

```python
#!/usr/bin/python3

import sys


def main():
    if len(sys.argv) == 1:
        print("Usage:")
        print("{} <arg1> <arg2> ...".format(sys.argv[0]))
        return

    for arg in sys.argv[1:]:
        print(arg)


if __name__ == "__main__":
    main()
```

As we can see, the CLI arguments are accessed from within the script and printed to
standard output:

```
$ python3 argv_demo.py 
Usage:
argv_demo.py <arg1> <arg2> ...
$ python3 argv_demo.py 1 2 3
1
2
3
```

However this way of implementing the command line interface is fairly low-level
and under-abstracted for more advanced use cases. For example, if we wanted to
implement subcommands or multiple options that may or may not be associated with values
we would need to do quite a bit of work to parse that list of arguments into
an internal form that we would be using further in the code. 

There are some Python modules to make it easier. The argparse module ships with
vanilla Python installation. [Click](https://click.palletsprojects.com/en/8.1.x/) 
is an open source project that provides further abstraction layer to enable 
setting up the CLI with very little code.

For demonstration purposes, let us assume that we want to develop a simple
script that takes one or more HTTP(S) URLs, tries fetching them with GET
requests and prints the HTTP response status codes to the user. We want to be 
able to pass either single URL or a list of URLs in a file. Futhermore, we want
to optionally set timeout duration and HTTP debug information.

Using argparse
--------------

When using [`argparse`](https://docs.python.org/3/library/argparse.html#module-argparse) 
module, we need to instantiate `ArgumentParser` object,
set it up with all the CLI arguments and use it to parse `sys.argv` (without
the first element). As a starting point, we can use Python REPL for prototyping.

```
$ python3
Python 3.10.6 (main, Aug 11 2022, 13:36:31) [Clang 13.1.6 (clang-1316.0.21.2.5)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import argparse
>>> parser = argparse.ArgumentParser(description="Simple HTTP URL Checker")
>>> parser
ArgumentParser(prog='', usage=None, description='Simple HTTP URL Checker', formatter_class=<class 'argparse.HelpFormatter'>, conflict_handler='error', add_help=True)
>>> parser.add_argument("--timeout", type=float, default=1.0, required=False, help="Timeout duration for HTTP GET request in seconds (default: 1.0)")
_StoreAction(option_strings=['--timeout'], dest='timeout', nargs=None, const=None, default=1.0, type=<class 'float'>, choices=None, required=False, help='Timeout duration for HTTP GET request in seconds (default: 1.0)', metavar=None)
>>> parser.add_argument("--verbose", default=False, required=False, action='store_true', help="Enable HTTP debug output (off by default)")
_StoreTrueAction(option_strings=['--verbose'], dest='verbose', nargs=0, const=True, default=False, type=None, choices=None, required=False, help='Enable HTTP debug output (off by default)', metavar=None)
>>> parser.add_argument("--url-list", required=True, nargs='*', help="HTTP URLs or files containing them (one URL per line)")
_StoreAction(option_strings=['--url-list'], dest='url_list', nargs='*', const=None, default=None, type=None, choices=None, required=True, help='HTTP URLs or files containing them (one URL per line)', metavar=None)
```

We have configured the optional `--verbose` and `--timeout` options, as well the required
`--url-list` argument that will take a list of URLs or files. Note that when setting up
the latter we call `add_argument()` with `nargs` set to `*` - this will tell the parser
that we expect a list of values that are to be parsed into Python list.

Now we can do a little testing on our argument parser.

```
>>> parser.print_help()
usage: [-h] [--timeout TIMEOUT] [--verbose] --url-list [URL_LIST ...]

Simple HTTP URL Checker

options:
  -h, --help            show this help message and exit
  --timeout TIMEOUT     Timeout duration for HTTP GET request in seconds (default: 1.0)
  --verbose             Enable HTTP debug output (off by default)
  --url-list [URL_LIST ...]
                        HTTP URLs or files containing them (one URL per line)
>>> parser.parse_args('--timeout 2.0 --verbose --url-list http://localhost:1313 http://localhost:1212'.split(' '))
Namespace(timeout=2.0, verbose=True, url_list=['http://localhost:1313', 'http://localhost:1212'])
>>> parser.parse_args('--url-list http://localhost:1313'.split(' '))
Namespace(timeout=1.0, verbose=False, url_list=['http://localhost:1313'])
```

It seems like it works properly. The complete script with `argparse`-based CLI is as following:

```python
#!/usr/bin/python3

import argparse
import http.client
import os
import sys
import logging

import requests

HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "sec-ch-ua": '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "cross-site",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
}

DEFAULT_TIMEOUT = 1.0


def check_url(url, timeout):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        return resp.status_code
    except Exception as e:
        return str(e)


def check_urls(urls, timeout, verbose):
    if verbose:
        # Based on: https://stackoverflow.com/a/16630836
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

    for u in urls:
        if u.startswith("http://") or u.startswith("https://"):
            print("{}\t{}".format(u, check_url(u, timeout)))
        else:
            if os.path.isfile(u):
                urls_from_file = []
                in_f = open(u, "r")
                lines = in_f.read().strip().split("\n")
                for line in lines:
                    if line.startswith("http://") or line.startswith("https://"):
                        urls_from_file.append(line)
                in_f.close()
                check_urls(urls_from_file, timeout, verbose)
            else:
                print("File not found: {}".format(u), file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Simple HTTP URL Checker")

    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        required=False,
        help="Timeout duration for HTTP GET request in seconds (default: {})".format(
            DEFAULT_TIMEOUT
        ),
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        required=False,
        help="Enable HTTP debug output (off by default)",
    )
    parser.add_argument(
        "--url-list",
        required=True,
        nargs="*",
        help="HTTP URLs or files containing them (one URL per line)",
    )

    args = parser.parse_args(sys.argv[1:])

    check_urls(args.url_list, args.timeout, args.verbose)


if __name__ == "__main__":
    main()
```

We can do some test runs to check that the CLI works correctly:

```
$ python3 url_scan_argparse.py -h
usage: url_scan_argparse.py [-h] [--timeout TIMEOUT] [--verbose] --url-list [URL_LIST ...]

Simple HTTP URL Checker

options:
  -h, --help            show this help message and exit
  --timeout TIMEOUT     Timeout duration for HTTP GET request in seconds (default: 1.0)
  --verbose             Enable HTTP debug output (off by default)
  --url-list [URL_LIST ...]
                        HTTP URLs or files containing them (one URL per line)
$ python3 url_scan_argparse.py --url-list https://trickster.dev https://trickster.dev/.git
https://trickster.dev	200
https://trickster.dev/.git	404
$ python3 url_scan_argparse.py --timeout 2.0
usage: url_scan_argparse.py [-h] [--timeout TIMEOUT] [--verbose] --url-list [URL_LIST ...]
url_scan_argparse.py: error: the following arguments are required: --url-list
$ python3 url_scan_argparse.py --verbose --url-list https://trickster.dev https://trickster.dev/.git
DEBUG:urllib3.connectionpool:Starting new HTTPS connection (1): trickster.dev:443
DEBUG:urllib3.connectionpool:https://trickster.dev:443 "GET / HTTP/1.1" 301 41
DEBUG:urllib3.connectionpool:Starting new HTTPS connection (1): www.trickster.dev:443
DEBUG:urllib3.connectionpool:https://www.trickster.dev:443 "GET / HTTP/1.1" 200 None
https://trickster.dev	200
DEBUG:urllib3.connectionpool:Starting new HTTPS connection (1): trickster.dev:443
DEBUG:urllib3.connectionpool:https://trickster.dev:443 "GET /.git HTTP/1.1" 301 45
DEBUG:urllib3.connectionpool:Starting new HTTPS connection (1): www.trickster.dev:443
DEBUG:urllib3.connectionpool:https://www.trickster.dev:443 "GET /.git HTTP/1.1" 404 None
https://trickster.dev/.git	404
```

Since this code is based on requests module it heeds `HTTP_PROXY` and `HTTPS_PROXY` environment
variables, which means it can be used to run some tests to check proxy pool suitability for a
particular target site.

Using Click
-----------

Modifying the code to use Click is not that difficult. First, we import it by putting the following
import statement at the top:

```python
import click
```

Then at them bottom we make `check_urls()` function to be an entry point of the script:

```python
if __name__ == "__main__":
    check_urls()
```

Next, we annotate this function with Click-specific annotations that will connect it to
the command line interface:

```python
@click.command()
@click.option(
    "--timeout",
    default=DEFAULT_TIMEOUT,
    help="Timeout duration for HTTP GET request in seconds",
)
@click.option(
    "--verbose",
    default=False,
    is_flag=True,
    help="Enable HTTP debug output (off by default)",
)
@click.option(
    "--url-list",
    required=True,
    multiple=True,
    help="HTTP URLs or files containing them (one URL per line)",
)
def check_urls(url_list, timeout, verbose):
```

Click module will make sure that value of `--timeout` from CLI will be assigned
to `timeout` function parameter. The same applies to other two arguments.

However there is one limitation. Although Click can take multiple values
for `--url-list` and parse them into Python array, it does not support 
the variadic form we had in the previous script. Each entry in the list will
have to have `--url-list` before it:

```
$ python3 url_scan_click.py --url-list https://trickster.dev --url-list https://trickster.dev/.git
https://trickster.dev	200
https://trickster.dev/.git	404
```


