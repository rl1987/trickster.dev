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

WRITEME: undoding hex/unicode string encoding

WRITEME: converting bracket notation to dot notation

WRITEME: removing empty statements
