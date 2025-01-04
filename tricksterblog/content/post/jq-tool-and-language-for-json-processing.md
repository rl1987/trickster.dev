+++
author = "rl1987"
title = "jq: tool and language for JSON processing"
date = "2025-01-31"
tags = []
draft = true
+++

Since JSON is the dominant data representation format for most of the modern 
RESTful APIs parsing, generation, modification and analysis of JSON documents 
is nothing new for many explorers of cyberspace. Indeed, there are libraries
and tools to wrangle JSONified data in pretty much all popular general purpose 
programming languages. But what about shell scripts? When one is programming
in Bash or Zsh it might be necessary to run some curl(1) snippet and extract 
parts of API response, but your standard Unix text processing tools - awk(1), 
sed(1), grep(1) and others largely predate JSON popularity and are not designed
with nested data trees in mind. [jq](https://jqlang.github.io/jq/) is CLI tool
that was designed to fill the gap here and address the need of making JSON
wrangling easier within the Unix/Linux environment. But jq is not merely a CLI
tool. Like AWK, it is also a Turing-complete domain specific language that lets
you implement arbitrarily complex (within limits of computability) JSON document
processing scripts.

One can install jq via the usual package managers:

* `brew install jq` on macOS with Homebrew.
* `apt-get install jq` on Debian and many Debian-based distributions.
* `pacman -S jq` on Arch Linux.
* `pkg install jq` on FreeBSD.

Furthermore, jq project ships ready-to-use binary files as part of their
[release deliverables](https://github.com/jqlang/jq/releases). To get the 
official Docker image with jq one can run `docker pull ghcr.io/jqlang/jq:latest`.

There is also [jqplay.org](https://jqplay.org/) - a web playground for playing
with jq language without installing anything.

The syntax of jq has similarities with JSON syntax. The very simplest thing one
can do in jq is pretty printing the input:

```
$ echo '{"x": 1, "y": 2}' | jq '.'
{
  "x": 1,
  "y": 2
}
```

By default jq makes output colored for easier reading. We used jq identity
statement as the first argument.

To extract a single field from JSON object we can use object identifier-index 
syntax - dot character with field name:

```
$ echo '{"x": 1, "y": 2}' | jq '.x'
1
```

This can be done across multiple levels:

```
$ echo '{"coord": {"x": 1, "y": 2}}' | jq '.coord.y'
2
```

Like other programming languages, JSON arrays can be indexed:

```
$ echo '{"coords": [{"x": 1.1, "y": 2.5}]}' | jq '.coords[0].y'
2.5
```

WRITEME: standard jq functions

WRITEME: simple API scraping example

https://hypebeastbaltics.com/products.json

WRITEME: using jq as a library - bindings for Python and other languages

