+++
author = "rl1987"
title = "jq: tool and language for JSON processing"
date = "2025-01-31"
tags = []
draft = true
+++

Since JSON is the dominant data representation format for most of the modern 
RESTful APIs. Some automation and devops tools (Terraform, AWS CLI, kubectl, 
etc.) optionally output data in JSON format to make it machine readable. Some
datasets (e.g. MRFs from health insurance companies) are available as JSON files.
For these reasons parsing, generation, modification and analysis of JSON documents 
is nothing new for many explorers of cyberspace. Indeed, there are libraries
and tools to wrangle JSONified data in pretty much all popular general purpose 
programming languages. But what about shell scripts? When one is programming
in Bash or Zsh it might be necessary to run some curl(1) snippet and extract 
parts of API response, but your standard Unix text processing tools - awk(1), 
sed(1), grep(1) and others largely predate JSON popularity and are not designed
with nested data trees in mind. [jq](https://jqlang.github.io/jq/) is CLI tool
that was designed to fill the gap here and address the need of making JSON
wrangling easier within the Unix/Linux environment. But it is not merely a CLI
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

We may want to create JSON object or list in jq language. Syntax to do so
is very similar to JSON notation:

```
$ jq --null-input '{a: 1, b: 2}'
{
  "a": 1,
  "b": 2
}
$ jq --null-input '[1,3,5,7,11]'
[
  1,
  3,
  5,
  7,
  11
]
```

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

Like in Python, arrays can be sliced by index range:

```
$ echo '[1,2,3,4,5]' | jq '.[1:3]'
[
  2,
  3
]
```

If used without indices, `[]` is iterator - it returns all values within the 
input list or object:

```
$ echo '[1,2,3,4,5]' | jq '.[]'   
1
2
3
4
5
$ echo '{"a": 1, "b": 2}' | jq '.[]'
1
2
```

Note that first index in the range is inclusive, but not the second one - second
index tells jq to extract values *up to* that index.

JSON data types have the same syntax in jq language as in JSON notation:

```
$ jq --monochrome-output --null-input 'null'   
null
$ jq --null-input '1.2'   
1.2
$ jq --null-input '"str"' 
"str"
$ jq --null-input 'false'
false
$ jq --null-input '{"latitude": 1.1, "longitude": 2.2}' 
{
  "latitude": 1.1,
  "longitude": 2.2
}
$ jq --null-input '["a", "b", "c"]' 
[
  "a",
  "b",
  "c"
]
```

Like in Unix environment, pipe character can be used to build pipelines of
operations:

```
$ jq --null-input '{"latitude": 1.1, "longitude": 2.2} | .latitude'
1.1
```

Comma character can be used to concatenate outputs from two or more operations
into single stream:

```
$ jq --null-input '{"latitude": 1.1, "longitude": 2.2} | .latitude, .longitude'  
1.1
2.2
```

Furthermore, jq language allows using question mark character as optional 
operator. Like in Swift programming language, this allows for parts of input
(e.g. a subtree in JSON document) to be missing without crashing the program.
If something is not missing, further operations will be executed. If it is 
missing, the entire chain of operations will return null value:

```
$ echo '{"coords": [{"x": 1.1, "y": 2.5}]}' | jq '.coords?[0].y'
2.5
$ echo '{"coords": [{"x": 1.1, "y": 2.5}]}' | jq '.coordinates?[0].y'
null
```

Like all the proper programming languages, jq has operators for basic math
operations:

```
$ jq --null-input '1 + 1'
2
$ jq --null-input '1 - 1'
0
$ jq --null-input '1 * 2'
2
$ jq --null-input '1 / 2'
0.5
$ jq --null-input '5 % 2' 
1
```

Multiplication operator can also be used to make repeated string:

```
$ jq --null-input '"cyber" * 3'
"cybercybercyber"
```

Furthermore, jq has some built-in functions for common computations and data
processing operations. For example, `length` is equivalent to Python's `len()`
function:

```
$ echo '"abc"' | jq 'length'   
3
$ echo '[1, 2, 3, 4]' | jq 'length'
4
```

The jq language does not have for or while loops. Instead, we are supposed to
use two brackets (`[]`) - iteration operator and/or `range` function:

```
$ jq --null-input 'range(100)'
0
1
2
3
4
...
96
97
98
99
100
$ jq --null-input '[range(100)]' | jq '.[] | . + 1000' | head
1000
1001
1002
1003
1004
1005
1006
1007
1008
1009
```

In jq language `map` is equivalent to `map()` in Python and `select` is
equivalent to `filter()`. 

This allows do implement data processing in FP-like manner: 

```
$ echo "[1000, 2000, 3000, 5000, 9001, 10240]" | jq '.[] | select(. > 9000)'
9001
10240
$ echo '["corpothieves", "must", "die"]' | jq 'map(length)'
[
  12,
  4,
  3
]
```

If we don't want to use `select` we can use regular if-then-else control flow
feature of jq:

```
$ echo "9001" | jq 'if . > 9000 then "over nine thousand" else "below 9000" end'
"over nine thousand"
```

There is also IEEE754 double precision floating point number support and you 
can do trigonometry and stuff. See the 
[documentation](https://jqlang.github.io/jq/manual/#builtin-operators-and-functions)
for a list of built-in functions available.

WRITEME: fizzbuzz in jq?


WRITEME: how to declare functions and write bigger programs

WRITEME: simple API scraping example

The jq codebase is in C, but the underlying "backend" of the language can be
used as a shared library - libjq. This would enable using it as DSL outside shell
scripts. But the thing is, unless what you do is in the realm of 
systems programming you probably do not want to use 
[libjq C API](https://github.com/jqlang/jq/wiki/C-API:-jv) in your own code.
For our convenience there are wrappers in higher level languages:

* [`jq` for Python](https://pypi.org/project/jq/) - available from PIP.
* [`jq-rs` for Rust](https://crates.io/crates/jq-rs)
* [`node-jq` for Node.js](https://www.npmjs.com/package/node-jq)
* [JSON::JQ for Perl](https://metacpan.org/pod/JSON::JQ)

For example, jq Python module makes API scraping code less tedious:

```
>>> import requests
>>> import jq
>>> resp = requests.get("https://hypebeastbaltics.com/products.json")
>>> jq.compile(".products[].title").input(text=resp.text).all()
['Used Arc`Teryx Bird Head Toque Beanie Red', 'Used Bape Blue Shark Silver Zip Tee', 'Used Supreme crew 96 tee khaki', 'Used Minus Two Cargo Pants Black Purple', 'Used Bape Blue Shark hoodie', 'Used Air Jordan 1 Low Grey Camo', 'Used Nike Air Force 1 Low Supreme Baroque Brown', 'Used Jordan 4 Retro University Blue', "Used Moncler Women's Blue Puffer Jacket with High Collar", 'Used Nike SB Dunk Low City of Love Burgundy Crush', 'Used adidas Yeezy Slide Bone (2022/2023 Restock)', 'Air Jordan 3 Retro Black Cat (2025)', "Used Moncler Guerledan Women's Fur Vest", 'Adidas Campus 80s Bape Brown', 'Used Yeezy Boost 380 Azure', 'Supreme Burberry Box Logo Tee White', 'Used Jordan 1 Mid SE Ice Blue (2023)', 'Used Nike SB Dunk Low April Skateboards', 'Used C.P. COMPANY DIAGONAL RAISED GOGGLE ZIP HOODIE', 'Used Stone Island Blue Button Up Shirt', 'Used Nike Dunk Low White Grey Navy Aqua Mini Swoosh', 'Used Jordan 1 Mid Multi-Color Swoosh Black', 'Used Nike Blazer Mid 77 Vintage Summit White Pink', 'Used  Nike Blazer Mid 77 Vintage Malachite Green', 'Used Nike Blazer Mid 77 White Volt', 'Used Nike Blazer Mid 77 LX White', 'Nike Dunk High AMBUSH Flash Lime', 'adidas Yeezy Foam RNNR Ochre', 'Air Jordan 1 Retro Low OG SP Travis Scott Velvet Brown', 'Timberland 6 Inch Zip Boot A-COLD-WALL Black']
```

[Gojq project](https://github.com/itchyny/gojq) reimplements the language in
pure Go and does not rely on the C codebase. It can be used as CLI tool and 
integrated into other software as library.

