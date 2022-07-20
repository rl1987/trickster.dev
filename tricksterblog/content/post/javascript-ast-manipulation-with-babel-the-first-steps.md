+++
author = "rl1987"
title = "JavaScript AST manipulation with Babel: the first steps"
date = "2022-07-21"
draft = true
tags = ["security", "reverse-engineering"]
+++

Previously on Trickster Dev:

* [Understanding Abstract Syntax Trees](/post/understanding-abstract-syntax-trees/)
* [JavaScript Obfuscation Techniques by Example](/post/javascript-obfuscation-techniques-by-example/)

When it comes to reverse engineering obfuscated JavaScript code there are two major approaches:

* Dynamic analysis - using debugger to step through the code and observing it's behaviour over time.
* Static analysis - performing source code analysis without running it, but parsing and analysing the code itself.

It is bad idea to rely exclusively on regular expressions and naive string manipulation to do web scraping.
The same applies to Javascript static analysis. Thus we will parse the JS code into Abstract Syntax Tree. This
will enable us to perform manipulations within a data model capable of representing the logical structure of the code.
We are going to write code to demonstrate how some of the basic obfuscation techniques could be reverted.

Our deobfuscation code will be based on [Babel](https://babeljs.io/) - a programmable toolkit for manipulating
JavaScript code. Typically it is being used in build systems of web-based software projects, but it has also 
been found to be quite useful by developers working on gray hat scraper/automation stuff
(not to be confused Babel from Python world that deals with internationalization/localisation stuff, and with 
OpenBabel the chemical data processing software).

Deobfuscation code we will be writing will work in three stages:

1. Parsing JS code into AST.
2. Modifying AST to undo obfuscations.
3. Regenerating JS code from AST.

Step 2 is where the bulk of work will be done.

Initially I wanted to do this in Python, but it turned out that there's no established Python module to regenerate
the JS code from AST. Altough some JS static analysis can be done in Python, JavaScript tooling and libraries are best
equipped to deal with JS code. However I don't typically code in JS so bear with me if code quality seems lacking.

Babel can be installed through NPM:

```
$ npm install --save-dev @babel/core @babel/cli
```

Let us consider the following code:

```javascript
fetch('https://hackerone.com/hacktivity', {
    headers: {
        'authority': 'hackerone.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'cache-control': 'max-age=0',
        'cookie': '_dd_s=',
        'referer': 'https://hackerone.com/',
        'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
});
```

We use the [DigitalOcean Code Minify](https://www.digitalocean.com/community/tools/minify) tool to remove
all the whitespace from this snippet:

```javascript
fetch("https://hackerone.com/hacktivity",{headers:{authority:"hackerone.com",accept:"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9","accept-language":"en-GB,en-US;q=0.9,en;q=0.8","cache-control":"max-age=0",cookie:"_dd_s=",referer:"https://hackerone.com/","sec-ch-ua":'".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',"sec-ch-ua-mobile":"?0","sec-ch-ua-platform":'"macOS"',"sec-fetch-dest":"document","sec-fetch-mode":"navigate","sec-fetch-site":"same-origin","sec-fetch-user":"?1","upgrade-insecure-requests":"1","user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"}});
```

[Screenshot 1](/2022-07-20_13.30.30.png)

Since minification is not really an obfuscation we can parse and regenerate the code without modifiying
the AST:

```
$ node
Welcome to Node.js v18.6.0.
Type ".help" for more information.
> const parser = require("@babel/parser");
undefined
> const fs = require("fs");
undefined
> const mjs = fs.readFileSync("minified.js", "utf-8");
undefined
> mjs
`fetch("https://hackerone.com/hacktivity",{headers:{authority:"hackerone.com",accept:"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9","accept-language":"en-GB,en-US;q=0.9,en;q=0.8","cache-control":"max-age=0",cookie:"_dd_s=",referer:"https://hackerone.com/","sec-ch-ua":'".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',"sec-ch-ua-mobile":"?0","sec-ch-ua-platform":'"macOS"',"sec-fetch-dest":"document","sec-fetch-mode":"navigate","sec-fetch-site":"same-origin","sec-fetch-user":"?1","upgrade-insecure-requests":"1","user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"}});`
> let ast = parser.parse(mjs);
undefined
> const generate = require("@babel/generator").default;
undefined
> generate(ast).code
'fetch("https://hackerone.com/hacktivity", {\n' +
  '  headers: {\n' +
  '    authority: "hackerone.com",\n' +
  '    accept: "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",\n' +
  '    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",\n' +
  '    "cache-control": "max-age=0",\n' +
  '    cookie: "_dd_s=",\n' +
  '    referer: "https://hackerone.com/",\n' +
  `    "sec-ch-ua": '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',\n` +
  '    "sec-ch-ua-mobile": "?0",\n' +
  `    "sec-ch-ua-platform": '"macOS"',\n` +
  '    "sec-fetch-dest": "document",\n' +
  '    "sec-fetch-mode": "navigate",\n' +
  '    "sec-fetch-site": "same-origin",\n' +
  '    "sec-fetch-user": "?1",\n' +
  '    "upgrade-insecure-requests": "1",\n' +
  '    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"\n' +
  '  }\n' +
  '});'
```

Since Babel pretty-prints the generated code by default it was trivial to undo the minification.

Applying hexadecimal string encoding to our test snippet yields the following obfuscated version:

```javascript
fetch('\x68\x74\x74\x70\x73\x3A\x2F\x2F\x68\x61\x63\x6B\x65\x72\x6F\x6E\x65\x2E\x63\x6F\x6D\x2F\x68\x61\x63\x6B\x74\x69\x76\x69\x74\x79',{headers:{'\x61\x75\x74\x68\x6F\x72\x69\x74\x79':'\x68\x61\x63\x6B\x65\x72\x6F\x6E\x65\x2E\x63\x6F\x6D','\x61\x63\x63\x65\x70\x74':'\x74\x65\x78\x74\x2F\x68\x74\x6D\x6C\x2C\x61\x70\x70\x6C\x69\x63\x61\x74\x69\x6F\x6E\x2F\x78\x68\x74\x6D\x6C\x2B\x78\x6D\x6C\x2C\x61\x70\x70\x6C\x69\x63\x61\x74\x69\x6F\x6E\x2F\x78\x6D\x6C\x3B\x71\x3D\x30\x2E\x39\x2C\x69\x6D\x61\x67\x65\x2F\x61\x76\x69\x66\x2C\x69\x6D\x61\x67\x65\x2F\x77\x65\x62\x70\x2C\x69\x6D\x61\x67\x65\x2F\x61\x70\x6E\x67\x2C\x2A\x2F\x2A\x3B\x71\x3D\x30\x2E\x38\x2C\x61\x70\x70\x6C\x69\x63\x61\x74\x69\x6F\x6E\x2F\x73\x69\x67\x6E\x65\x64\x2D\x65\x78\x63\x68\x61\x6E\x67\x65\x3B\x76\x3D\x62\x33\x3B\x71\x3D\x30\x2E\x39','\x61\x63\x63\x65\x70\x74\x2D\x6C\x61\x6E\x67\x75\x61\x67\x65':'\x65\x6E\x2D\x47\x42\x2C\x65\x6E\x2D\x55\x53\x3B\x71\x3D\x30\x2E\x39\x2C\x65\x6E\x3B\x71\x3D\x30\x2E\x38','\x63\x61\x63\x68\x65\x2D\x63\x6F\x6E\x74\x72\x6F\x6C':'\x6D\x61\x78\x2D\x61\x67\x65\x3D\x30','\x63\x6F\x6F\x6B\x69\x65':'\x5F\x64\x64\x5F\x73\x3D','\x72\x65\x66\x65\x72\x65\x72':'\x68\x74\x74\x70\x73\x3A\x2F\x2F\x68\x61\x63\x6B\x65\x72\x6F\x6E\x65\x2E\x63\x6F\x6D\x2F','\x73\x65\x63\x2D\x63\x68\x2D\x75\x61':'\x22\x2E\x4E\x6F\x74\x2F\x41\x29\x42\x72\x61\x6E\x64\x22\x3B\x76\x3D\x22\x39\x39\x22\x2C\x20\x22\x47\x6F\x6F\x67\x6C\x65\x20\x43\x68\x72\x6F\x6D\x65\x22\x3B\x76\x3D\x22\x31\x30\x33\x22\x2C\x20\x22\x43\x68\x72\x6F\x6D\x69\x75\x6D\x22\x3B\x76\x3D\x22\x31\x30\x33\x22','\x73\x65\x63\x2D\x63\x68\x2D\x75\x61\x2D\x6D\x6F\x62\x69\x6C\x65':'\x3F\x30','\x73\x65\x63\x2D\x63\x68\x2D\x75\x61\x2D\x70\x6C\x61\x74\x66\x6F\x72\x6D':'\x22\x6D\x61\x63\x4F\x53\x22','\x73\x65\x63\x2D\x66\x65\x74\x63\x68\x2D\x64\x65\x73\x74':'\x64\x6F\x63\x75\x6D\x65\x6E\x74','\x73\x65\x63\x2D\x66\x65\x74\x63\x68\x2D\x6D\x6F\x64\x65':'\x6E\x61\x76\x69\x67\x61\x74\x65','\x73\x65\x63\x2D\x66\x65\x74\x63\x68\x2D\x73\x69\x74\x65':'\x73\x61\x6D\x65\x2D\x6F\x72\x69\x67\x69\x6E','\x73\x65\x63\x2D\x66\x65\x74\x63\x68\x2D\x75\x73\x65\x72':'\x3F\x31','\x75\x70\x67\x72\x61\x64\x65\x2D\x69\x6E\x73\x65\x63\x75\x72\x65\x2D\x72\x65\x71\x75\x65\x73\x74\x73':'\x31','\x75\x73\x65\x72\x2D\x61\x67\x65\x6E\x74':'\x4D\x6F\x7A\x69\x6C\x6C\x61\x2F\x35\x2E\x30\x20\x28\x4D\x61\x63\x69\x6E\x74\x6F\x73\x68\x3B\x20\x49\x6E\x74\x65\x6C\x20\x4D\x61\x63\x20\x4F\x53\x20\x58\x20\x31\x30\x5F\x31\x35\x5F\x37\x29\x20\x41\x70\x70\x6C\x65\x57\x65\x62\x4B\x69\x74\x2F\x35\x33\x37\x2E\x33\x36\x20\x28\x4B\x48\x54\x4D\x4C\x2C\x20\x6C\x69\x6B\x65\x20\x47\x65\x63\x6B\x6F\x29\x20\x43\x68\x72\x6F\x6D\x65\x2F\x31\x30\x33\x2E\x30\x2E\x30\x2E\x30\x20\x53\x61\x66\x61\x72\x69\x2F\x35\x33\x37\x2E\x33\x36'}})
```

[Screenshot 2](/2022-07-20_15.52.41.png)

Before we proceed with writing code to deobfuscate this, let us do a quick experiment on 
[AST Explorer](https://astexplorer.net/). Make sure that JavaScript language is chosen in
language dropdown and choose `@babel/parser` in parser dropdown. Then let us check the
AST-level difference between the following JS statements:

```javascript
console.log("AAA");
console.log("\x41\x41\x41");
```

[Screenshot 3](/2022-07-20_16.01.29.png)

We see that in hex-encoded version of the `StringLiteral` the `extra.raw` field is a
not the same as `extra.raw`, whereas they are the same in a normal version 
of the string (except `extra.raw` being enclosed in double quotes). This gives us
an idea on how to undo the hex encoding: when processing the AST, let us set `raw`
based on the clean form of a string in `rawValue` field.

To manipulate the Abstract Syntax Tree, we are going to apply the Visitor design
pattern that entails a degree of decoupling of code that does manipulation of tree elements
from the underlying data structure. Babel has us covered here, since we don't need to
worry about traversing the AST and merely have to call `traverse()` with a callback function for a
type of AST node that we want to modify.

Code that undoes string hex-encoding is as follows:

```javascript
const fs = require("fs");

const parser = require("@babel/parser");
const generate = require("@babel/generator").default;
const traverse = require("@babel/traverse").default;

let hjs = fs.readFileSync("hexcoded.js", "utf-8");

const ast = parser.parse(hjs);

traverse(ast, {
    StringLiteral: function(path) {
        path.node.extra.raw = "\"" + path.node.extra.rawValue + "\"";
    }
});

let clean = generate(ast).code;

fs.writeFileSync("clean1.js", clean);
```

Fairly simple, right?

Now what if we wanted to convert bracket notation into dot notation? That is, we could have
statements like this:

```javascript
console["log"]("AAA");
```

And we wanted them to be like this:

```javascript
console.log("AAA");
```

For the sake of the example, let us try cleaning up the following code:

```javascript
console.log("AAA");
console["log"]("AAA");

let o = {};
o["a"] = 42;
```

Note that we specifically want to get rid of bracket notation for function calls, but not
for object member assignment.

Let us put both statements into AST Explorer and see how do they differ at AST level.

[Screenshot 4](/2022-07-20_17.28.55.png)

We see that in both cases `CallExpression` has `MemberExpression` at `callee` field, but
there's a difference at `MemberExpression` level: in the case of dot notation there's
`Identifier` object at `property`, but in the case of bracket notation it's a
`StringLiteral`. Furthermore, `computed` is false when dot notation is used and true
when bracket notation is used.

So we write some code to find all parts of AST that match the latter pattern and fix
it to be like the former.

```javascript
const fs = require("fs");

const parser = require("@babel/parser");
const generate = require("@babel/generator").default;
const traverse = require("@babel/traverse").default;
const types = require("@babel/types");

let js = fs.readFileSync("brackets.js", "utf-8");

const ast = parser.parse(js);

traverse(ast, {
    CallExpression: function(path) {
        let prop = path.node.callee.property;

        if (types.isStringLiteral(prop)) {
          path.node.callee.property = types.Identifier(prop.value);
          path.node.callee.computed = false;
        }
    }
});

let clean = generate(ast).code;

fs.writeFileSync("clean2.js", clean);
```

Running this script converts our sample code into the following:

```javascript
console.log("AAA");
console.log("AAA");
let o = {};
o["a"] = 42;
```

Since we did matching on `CallExpression` it did not touch the last statement that involves
assigning member a of JS object.

Lastly, let us consider the following code:

```javascript
;;;;;console.log("123");;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
```

This has way too many semi-colons that we want to remove. Turns out each extra semicolon
is represented by `EmptyStatement` in a Babel AST data model.

[Screenshot 5](/2022-07-20_17.14.15.png)

Thus we simply remove the
`EmptyStatement` nodes when traversing the AST:

```javascript
const fs = require("fs");

const parser = require("@babel/parser");
const generate = require("@babel/generator").default;
const traverse = require("@babel/traverse").default;

let js = fs.readFileSync("too_many_semicolons.js", "utf-8");

const ast = parser.parse(js);

traverse(ast, {
    EmptyStatement: function(path) {
        path.remove();
    }
});

let clean = generate(ast).code;

fs.writeFileSync("clean3.js", clean);
```

Running this gives us a cleaned up version of the code:

```javascript
console.log("123");
```


