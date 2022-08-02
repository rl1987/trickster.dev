+++
author = "rl1987"
title = "JavaScript AST manipulation with Babel: extracting hardcoded data"
date = "2022-08-02"
draft = true
tags = ["security", "reverse-engineering", "javascript", "scraping"]
+++

When scraping the web one sometimes comes across data being hardcoded in JS snippets.
One could be using regular expressions or naive string operations to extract it. 
However, it is also possible to parse JavaScript code into Abstract Syntax Tree to 
extract the hardcoded data in a more structured way than by using simple string
processing. Let us go through couple of examples.

Suppose you were scraping some site and came across to JS code similar to
following [example from Meta developer portal](https://developers.facebook.com/docs/javascript/examples):

```javascript
FB.ui({
  method: 'share',
  href: 'https://developers.facebook.com/docs/'
}, function(response){});
```

We want to extract the URL that is being shared. Putting this snippet into
[AST Explorer](https://astexplorer.net/) converts it to AST that we can look into.

[Screenshot 1](/2022-08-02_18.12.29.png)

We can see that each key-value pair in JS object is represented by `ObjectProperty` node
with `method` boolean property being false. Key is represented by `Identifier` node and
value (in this case) is represented by a `StringLiteral`). This informs us how to write
Node.JS script based on Babel to dig out the URL being shared:

```javascript
const fs = require("fs");

const parser = require("@babel/parser");
const traverse = require("@babel/traverse").default;

let js = fs.readFileSync("fb_example.js", "utf-8");

const ast = parser.parse(js);

var url = null;

traverse(ast, {
    ObjectProperty: function(path) {
        if (!path.node.method && path.node.key.name == "href") {
            url = path.node.value.value;
        }
    }
});

console.log(url);
```

If there was more key-value pairs that were interested in it would be fairly trivial to
update the code accordingly.

Another form of hardcoded data you may run across is the one that is almost-JSON:

```javascript
    var data = [
    {
        "tags": [
            "change",
            "deep-thoughts",
            "thinking",
            "world"
        ],
        "author": {
            "name": "Albert Einstein",
            "goodreads_link": "/author/show/9810.Albert_Einstein",
            "slug": "Albert-Einstein"
        },
        "text": "\u201cThe world as we have created it is a process of our thinking. It cannot be changed without changing our thinking.\u201d"
    },
    {
        "tags": [
            "abilities",
            "choices"
        ],
        "author": {
            "name": "J.K. Rowling",
            "goodreads_link": "/author/show/1077326.J_K_Rowling",
            "slug": "J-K-Rowling"
        },
        "text": "\u201cIt is our choices, Harry, that show what we truly are, far more than our abilities.\u201d"
    },
```

See: http://quotes.toscrape.com/js/

[Screenshot 2](/2022-08-02_18.28.50.png)
[Screenshot 3](/2022-08-02_18.29.11.png)

Once again, let us investigate the AST through AST Explorer web app.

[Screenshot 4](/2022-08-02_18.31.17.png)
[Screenshot 5](/2022-08-02_18.31.28.png)
[Screenshot 6](/2022-08-02_18.33.52.png)

Each member of `data` array is represented by `ObjectExpression`. Under each `ObjectExpression` node,
there's `ObjectProperty` for each key-value pair. This is similar to previous example now, except that
key is represented by `StringLiteral` node and value is not necessarily represented as `StringLiteral`
due to nestedness of the structure. For example, list of tags is represented by `ArrayExpression`
that has `StringLiteral`s as child nodes.

To keep things short and up to the point, we will save the above JS snippet to a file and process it from there.

```javascript
const fs = require("fs");

const parser = require("@babel/parser");
const traverse = require("@babel/traverse").default;
const types = require("@babel/types");

let js = fs.readFileSync("quotes.js", "utf-8");

const ast = parser.parse(js);

var rows = [];

traverse(ast, {
    ArrayExpression: function(path) {
        let arrayNode = path.node;
        for (idx  = 0; idx < arrayNode.elements.length; idx++) {
            let node = arrayNode.elements[idx];
            var row = {};

            if (node.properties === undefined)
                continue;

            for (i = 0; i < node.properties.length; i++) {
                let property = node.properties[i];
                if (property.key.value == "text") {
                    row["text"] = property.value.value;
                } else if (property.key.value == "author") {
                    let author_properties = property.value.properties;

                    for (j = 0; j < author_properties.length; j++) {
                        let author_property = author_properties[j];
                        if (author_property.key.value == "name") {
                            row["author_name"] = author_property.value.value;
                        }
                    }
                }
            }

            rows.push(row);
        }
    }
});

console.log(rows);
```

In this case we match our visitor function to `ArrayExpression` as it's the only node of this type
in the code being processed. Then we go iterate across `ArrayExpression` node children that represent
elements in the array - each of them is `ObjectExpression`. Each of these is treated as subtree that
correspond to a row of data we want to extract - author name and quote text for each quote. These
pieces of data are being extracted by applying fairly simple traversal of the subtree.

