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
wrangling viable within the Unix/Linux environment. But jq is not merely a CLI
tool. Like AWK, it is also a Turing-complete domain specific language that lets
you implement arbitrarily complex (within limits of computability) JSON document
processing scripts.

WRITEME: how to install, jqplay.org

WRITEME: basic syntax

WRITEME: standard jq functions

WRITEME: simple API scraping example

WRITEME: using jq as a library - bindings for Python and other languages

