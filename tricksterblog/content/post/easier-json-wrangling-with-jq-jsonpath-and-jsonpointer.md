+++
author = "rl1987"
title = "Easier JSON wrangling with jq, JSONPath and JSONPointer"
date = "2022-01-09"
draft = true
tags = ["automation", "python"]
+++

In this day and age, JSON is the dominating textual format for information exchange between software systems.
JSON is based on key-value pairs. Key is always a string, but values can be objects (dictionaries), arrays, 
numbers, booleans, strings or nulls. Common problem that software developers are running into is that
JSON tree structures can be deeply nested with parts that may or may not be present. This can lead to 
tedious, awkward code. Let us get familiar with three ways to make JSON wrangling easier.

Let us download a JSON document for experimentation.

```
$ curl -s https://www.redbullshopus.com/products.json > products.json
```

jq - CLI tool and Domain Specific Language for JSON processing
--------------------------------------------------------------

[jq](https://stedolan.github.io/jq/) is a command line tool that is meant to be sed(1) for JSON processing.
Think of it as a filter that reads JSON string through standard input and outputs processed results through
standard output.

A simple trick to pretty-print JSON string in Unix/Linux command line is a follows:

```
$ cat products.json | python3 -m json.tool
{
  "products": [
    {
      "id": 6619238891591,
      "title": "Red Bull KTM Racing Team Colorswitch Hat",
      "handle": "red-bull-ktm-racing-team-colorswitch-hat",
      "body_html": "<p>Red Bull KTM Racing Team Colorswitch Hat for Men &amp; Women.</p>\n<ul>\n<li>One Size Fits Most</li>\n<li>Unisex</li>\n</ul>",
      "published_at": "2022-01-06T07:33:16-08:00",
      "created_at": "2022-01-06T07:33:15-08:00",
      "updated_at": "2022-01-06T07:33:44-08:00",
      "vendor": "Red Bull KTM Racing Team",
      "product_type": "Hats",
      "tags": [
        "Accessories",
        "Cap",
        "Hat",
        "Head wear",
        "Headwear",
        "KTM",
        "Ladies",
        "Men",
        "Mens",
        "Red Bull KTM Racing Team",
        "Unisex",
        "Women",
        "Womens"
      ],
      "variants": [
        {
          "id": 39565425770567,
          "title": "One Size / Navy",
          "option1": "One Size",
...
```

This can be reproduced with jq identity operator:

```
$ cat products.json | jq '.'
```

One can chain JSON keys and use indices to extract parts of JSON document:

```
$ cat products.json | jq '.products[0].title'
"Red Bull KTM Racing Team Colorswitch Hat"
```

In the document we are processing, we have an array of product dictionaries at key `products` in the root dictionary.
What if we want to extract all titles? This can be done with jq iterator:

```
$ cat products.json | jq '.products[].title'
"Red Bull KTM Racing Team Colorswitch Hat"
"Red Bull KTM Racing Team Stone Flat Hat"
"Red Bull KTM Racing Team Twist Flat Hat"
"Red Bull KTM Racing Team Women's Official Teamline T-Shirt"
"Red Bull KTM Racing Team Official Teamline T-Shirt"
"Red Bull KTM Racing Team Official Teamline Polo Shirt"
"Red Bull KTM Racing Team Official Teamline Shirt"
"Red Bull KTM Racing Team Official Teamline Hoodie"
"Red Bull KTM Racing Team Half Zip Sweater"
"Red Bull KTM Racing Team Official Teamline Softshell Jacket"
"Red Bull KTM Racing Team Official Teamline Windbreaker"
"Red Bull KTM Racing Team Official Teamline Winter Jacket"
"Red Bull KTM Racing Team Athletic Hat"
"Red Bull KTM Racing Team New Era 9FIFTY Stretch Hat"
"RB Leipzig Arrow Drink Bottle"
"Wings for Life Lokai Bracelet"
"Red Bull KTM Racing Team Pop Socket"
"Red Bull KTM Racing Team Sticker Pack"
"Red Bull KTM Racing Team Musquin No Tee"
"New York Red Bulls Mitchell & Ness Classic Snapback"
"Red Bull Rampage Camo Women's Tank"
"Red Bull KTM Factory Racing Knit Runner"
"Red Bull KTM Factory Racing Logo Tee"
"Red Bull KTM Racing Team Sticker"
"Red Bull Spect Solo Goggles"
"Red Bull Soar Goggles"
"Red Bull Spect Sight Goggles"
"Red Bull Spect Rush Goggles"
"Red Bull Spect Magnetron Slick Goggles"
"Red Bull Spect Magnetron-019 Goggles"
```

Right now we're extracting just the product title, but in practical projects we will need to extract more fields. 
For the sake of example, let us extract the following fields and group them together for each product: `title`, `id` and
`handle`. We will be using pipe (`|`) and object construction (`{}`):

```
$ cat products.json | jq '.products[] | {"title": .title, "id": .id, "handle": .handle}'
{
  "title": "Red Bull KTM Racing Team Colorswitch Hat",
  "id": 6619238891591,
  "handle": "red-bull-ktm-racing-team-colorswitch-hat"
}
{
  "title": "Red Bull KTM Racing Team Stone Flat Hat",
  "id": 6619238498375,
  "handle": "red-bull-ktm-racing-team-stone-flat-hat"
}
{
  "title": "Red Bull KTM Racing Team Twist Flat Hat",
  "id": 6619238367303,
  "handle": "red-bull-ktm-racing-team-twist-flat-hat"
}
{
  "title": "Red Bull KTM Racing Team Women's Official Teamline T-Shirt",
  "id": 6619238105159,
  "handle": "red-bull-ktm-racing-team-womens-official-teamline-t-shirt"
}
{
  "title": "Red Bull KTM Racing Team Official Teamline T-Shirt",
  "id": 6619237941319,
  "handle": "red-bull-ktm-racing-team-official-teamline-t-shirt-1"
}
```

We notice that the output isn't quite right. This is not a valid JSON, as JSON objects are not contained in the array.
This can be fixed by using array construction (`[]`):

```
$ cat products.json | jq '[.products[] | {"title": .title, "id": .id, "handle": .handle}]'
[
  {
    "title": "Red Bull KTM Racing Team Colorswitch Hat",
    "id": 6619238891591,
    "handle": "red-bull-ktm-racing-team-colorswitch-hat"
  },
  {
    "title": "Red Bull KTM Racing Team Stone Flat Hat",
    "id": 6619238498375,
    "handle": "red-bull-ktm-racing-team-stone-flat-hat"
  },
  {
    "title": "Red Bull KTM Racing Team Twist Flat Hat",
    "id": 6619238367303,
    "handle": "red-bull-ktm-racing-team-twist-flat-hat"
  },
...
```

Now we have a proper JSON document with JSON array as topmost element. What if we want CSV instead? This can be
achieved by forming arrays with all values lined up and piping them into `@csv` operator:

```
$ cat products.json | jq --raw-output '.products[] | [.title,.id,.handle] | @csv'
"Red Bull KTM Racing Team Colorswitch Hat",6619238891591,"red-bull-ktm-racing-team-colorswitch-hat"
"Red Bull KTM Racing Team Stone Flat Hat",6619238498375,"red-bull-ktm-racing-team-stone-flat-hat"
"Red Bull KTM Racing Team Twist Flat Hat",6619238367303,"red-bull-ktm-racing-team-twist-flat-hat"
"Red Bull KTM Racing Team Women's Official Teamline T-Shirt",6619238105159,"red-bull-ktm-racing-team-womens-official-teamline-t-shirt"
"Red Bull KTM Racing Team Official Teamline T-Shirt",6619237941319,"red-bull-ktm-racing-team-official-teamline-t-shirt-1"
"Red Bull KTM Racing Team Official Teamline Polo Shirt",6619237515335,"red-bull-ktm-racing-team-official-teamline-polo-shirt"
"Red Bull KTM Racing Team Official Teamline Shirt",6619237220423,"red-bull-ktm-racing-team-official-teamline-shirt-1"
"Red Bull KTM Racing Team Official Teamline Hoodie",6619236892743,"red-bull-ktm-racing-team-official-teamline-hoodie-1"
"Red Bull KTM Racing Team Half Zip Sweater",6619236401223,"red-bull-ktm-racing-team-half-zip-sweater"
"Red Bull KTM Racing Team Official Teamline Softshell Jacket",6619235942471,"red-bull-ktm-racing-team-official-teamline-softshell-jacket-1"
"Red Bull KTM Racing Team Official Teamline Windbreaker",6619235582023,"red-bull-ktm-racing-team-official-teamline-windbreaker"
"Red Bull KTM Racing Team Official Teamline Winter Jacket",6619234861127,"red-bull-ktm-racing-team-official-teamline-winter-jacket"
"Red Bull KTM Racing Team Athletic Hat",69601558540,"red-bull-ktm-racing-team-athletic-hat"
"Red Bull KTM Racing Team New Era 9FIFTY Stretch Hat",4430841446471,"red-bull-ktm-racing-team-new-era-9fifty-stretch-hat"
"RB Leipzig Arrow Drink Bottle",6604396527687,"rb-leipzig-arrow-drink-bottle"
"Wings for Life Lokai Bracelet",1482846011463,"wings-for-life-lokai-bracelet"
"Red Bull KTM Racing Team Pop Socket",1305585745991,"red-bull-ktm-racing-team-pop-socket"
"Red Bull KTM Racing Team Sticker Pack",69870256140,"red-bull-ktm-racing-team-sticker-pack"
"Red Bull KTM Racing Team Musquin No Tee",69600313356,"red-bull-ktm-racing-team-musquin-no-tee"
"New York Red Bulls Mitchell & Ness Classic Snapback",11735324044,"new-york-red-bulls-fleece-clear-script"
"Red Bull Rampage Camo Women's Tank",11710054476,"red-bull-rampage-camo-womens-tank"
"Red Bull KTM Factory Racing Knit Runner",9000667276,"red-bull-ktm-factory-racing-knit-runner"
"Red Bull KTM Factory Racing Logo Tee",3250440771,"red-bull-ktm-factory-racing-logo-tee"
"Red Bull KTM Racing Team Sticker",1588450197575,"red-bull-ktm-racing-team-sticker"
"Red Bull Spect Solo Goggles",6610181226567,"red-bull-spect-solo-goggles"
"Red Bull Soar Goggles",6610180767815,"red-bull-soar-goggles"
"Red Bull Spect Sight Goggles",6610180309063,"red-bull-spect-sight-goggles"
"Red Bull Spect Rush Goggles",6610179850311,"red-bull-spect-rush-goggles"
"Red Bull Spect Magnetron Slick Goggles",6610178932807,"red-bull-spect-magnetron-slick-goggles"
"Red Bull Spect Magnetron-019 Goggles",6610178474055,"red-bull-spect-magnetron-019-goggles"
```

Note that we also used `--raw-output` CLI argument to get an output that is not formatted as JSON strings (i.e. without
surrounding double quotes).

To learn more about jq, see:

* Official jq tutorial at https://stedolan.github.io/jq/tutorial/
* jq manual at https://stedolan.github.io/jq/manual/
* jqplay - a jq playground https://jqplay.org/

JSONPath - equivalent of XPath for JSON
---------------------------------------

For extracting fields from XML document there is XPath query language that enables developers to narrow down the
exact parts of XML tree they need extracted. Proposal 
[draft-ietf-jsonpath-base-02](https://www.ietf.org/archive/id/draft-ietf-jsonpath-base-02.txt) proposes
JSONPath - the XPath equivalent for JSON.

Let us experiment with [jsonpath-ng](https://github.com/h2non/jsonpath-ng) - a Python module that implements JSONPath.

First, let us launch a Python REPL and load the JSON file we have downloaded:

```
$ python3
Python 3.9.9 (main, Nov 21 2021, 03:22:47) 
[Clang 12.0.0 (clang-1200.0.32.29)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import json
>>> in_f = open("products.json", "r")
>>> json_dict = json.load(in_f)
>>> in_f.close()
```

Also, let us import some stuff from jsonpath-ng module:

```
>>> from jsonpath_ng import jsonpath, parse
```

Now, let's find product titles with JSONPath:

```
>>> jsonpath_expr = parse("products[*].title")
>>> matches = jsonpath_expr.find(json_dict)
>>> for m in matches:
...     print(m.value)
...
Red Bull KTM Racing Team Colorswitch Hat
Red Bull KTM Racing Team Stone Flat Hat
Red Bull KTM Racing Team Twist Flat Hat
Red Bull KTM Racing Team Women's Official Teamline T-Shirt
Red Bull KTM Racing Team Official Teamline T-Shirt
Red Bull KTM Racing Team Official Teamline Polo Shirt
Red Bull KTM Racing Team Official Teamline Shirt
Red Bull KTM Racing Team Official Teamline Hoodie
Red Bull KTM Racing Team Half Zip Sweater
Red Bull KTM Racing Team Official Teamline Softshell Jacket
Red Bull KTM Racing Team Official Teamline Windbreaker
Red Bull KTM Racing Team Official Teamline Winter Jacket
Red Bull KTM Racing Team Athletic Hat
Red Bull KTM Racing Team New Era 9FIFTY Stretch Hat
RB Leipzig Arrow Drink Bottle
Wings for Life Lokai Bracelet
Red Bull KTM Racing Team Pop Socket
Red Bull KTM Racing Team Sticker Pack
Red Bull KTM Racing Team Musquin No Tee
New York Red Bulls Mitchell & Ness Classic Snapback
Red Bull Rampage Camo Women's Tank
Red Bull KTM Factory Racing Knit Runner
Red Bull KTM Factory Racing Logo Tee
Red Bull KTM Racing Team Sticker
Red Bull Spect Solo Goggles
Red Bull Soar Goggles
Red Bull Spect Sight Goggles
Red Bull Spect Rush Goggles
Red Bull Spect Magnetron Slick Goggles
Red Bull Spect Magnetron-019 Goggles
```

Since JSONPath standard is still being developed and does not have a proper standard we will not discuss it further.
However, I would advice to keep it in mind for future use when it is more established.

JSONPointer - format for querying JSON documents
------------------------------------------------

WRITEME

