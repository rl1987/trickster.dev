+++
author = "rl1987"
title = "Solving a simple JS challenge with sandboxing"
date = "2023-09-15"
tags = ["scraping", "reverse-engineering", "python", "javascript"]
+++

Many antibot solutions involve client-side JavaScript challenges - performing
randomised computation, probing browser environment and so on. That may pose
an obstacle for web scraper and automation bot development. In some cases this
involves heavily obfuscated or even virtualised code that is hard to reverse
engineer. Ideally we want to fully understand and reproduce the challenge in
our code, but that is not always easy or worth the time and effort. A simpler
way to deal with JS challenges is technique known as sandboxing - creating
an artificial, isolated environment to run the challenge code with
little to no modifications and extracting the outputs from the code (e.g. HTTP
headers or cookies). In this post we will go through a simple example of this 
technique.

For the sake of example, we need a sample of JS challenge code. Some sites, 
such as OpenCorporates provide us with a simple one to play with:

```
$ curl https://opencorporates.com
<html><head><script type="text/javascript"><!--
function leastFactor(n) {
 if (isNaN(n) || !isFinite(n)) return NaN;
 if (typeof phantom !== 'undefined') return 'phantom';
 if (typeof module !== 'undefined' && module.exports) return 'node';
 if (n==0) return 0;
 if (n%1 || n*n<2) return 1;
 if (n%2==0) return 2;
 if (n%3==0) return 3;
 if (n%5==0) return 5;
 var m=Math.sqrt(n);
 for (var i=7;i<=m;i+=30) {
  if (n%i==0)      return i;
  if (n%(i+4)==0)  return i+4;
  if (n%(i+6)==0)  return i+6;
  if (n%(i+10)==0) return i+10;
  if (n%(i+12)==0) return i+12;
  if (n%(i+16)==0) return i+16;
  if (n%(i+22)==0) return i+22;
  if (n%(i+24)==0) return i+24;
 }
 return n;
}
function go() {
 var p=1612862479081; var s=3718246712; var n;
if ((s >> 12) & 1)/*
*13;
*/p+=120385074*15;
else 
p-=/*
else p-=
*/126371223* 13;	if ((s >> 6) & 1)/*
*13;
*/p+=159919203* 9;
else 	p-=
142123288*	7;if ((s >> 11) & 1)/*
*13;
*/p+=135381145*/*
p+= */12;
else /*
*13;
*/p-=/*
else p-=
*/79540378* 12;	if ((s >> 13) & 1) p+=/*
p+= */86227786*
14; else  p-=/* 120886108*
*/78525417*
14;/*
p+= */if ((s >> 14) & 1) p+=/* 120886108*
*/104707476*/*
else p-=
*/17;/*
else p-=
*/else 	p-= 23237263*
15;
 p-=3141693876;
 n=leastFactor(p);
{ document.cookie="KEY="+n+"*"+p/n+":"+s+":2460963898:1;path=/;";
  document.location.reload(true); }
}
//--></script></head>
<body onload="go()">
Loading...
</body>
</html>
```

The HTML document calls the `go()` function when it is loaded. The `go()` 
function calls `leastFactor()` to perform some checks and computations. There
are some funny comments meant to throw off people who are using regular 
expresions to clean up code, but we can get rid of them at AST level. Let
us copy-paste the JS code into [AST Explorer](https://astexplorer.net/) and 
apply the following Babel transform:

```javascript
export default function (babel) {
  const { types: t } = babel;
  
  return {
    name: "ast-transform", // not required
    visitor: {
      "Program|IfStatement|Expression|ExpressionStatement"(path) {
        t.removeComments(path.node);
      }
    }
  };
}
```

This yields the following code with junk comments removed:

```javascript
function leastFactor(n) {
  if (isNaN(n) || !isFinite(n)) return NaN;
  if (typeof phantom !== 'undefined') return 'phantom';
  if (typeof module !== 'undefined' && module.exports) return 'node';
  if (n == 0) return 0;
  if (n % 1 || n * n < 2) return 1;
  if (n % 2 == 0) return 2;
  if (n % 3 == 0) return 3;
  if (n % 5 == 0) return 5;
  var m = Math.sqrt(n);

  for (var i = 7; i <= m; i += 30) {
    if (n % i == 0) return i;
    if (n % (i + 4) == 0) return i + 4;
    if (n % (i + 6) == 0) return i + 6;
    if (n % (i + 10) == 0) return i + 10;
    if (n % (i + 12) == 0) return i + 12;
    if (n % (i + 16) == 0) return i + 16;
    if (n % (i + 22) == 0) return i + 22;
    if (n % (i + 24) == 0) return i + 24;
  }

  return n;
}

function go() {
  var p = 1612862479081;
  var s = 3718246712;
  var n;
  if (s >> 12 & 1) p += 120385074 * 15;else p -= 126371223 * 13;
  if (s >> 6 & 1) p += 159919203 * 9;else p -= 142123288 * 7;
  if (s >> 11 & 1) p += 135381145 * 12;else p -= 79540378 * 12;
  if (s >> 13 & 1) p += 86227786 * 14;else p -= 78525417 * 14;
  if (s >> 14 & 1) p += 104707476 * 17;else p -= 23237263 * 15;
  p -= 3141693876;
  n = leastFactor(p);
  {
    document.cookie = "KEY=" + n + "*" + p / n + ":" + s + ":2460963898:1;path=/;";
    document.location.reload(true);
  }
}
```

[Screenshot](/2023-09-09_19.05.00.png)

Aside from some random computations with random numbers, there are two things
to notice here. First are checks for symptoms of automation on the top of 
`leastFactor()` function:

```javascript
  if (typeof phantom !== 'undefined') return 'phantom';
  if (typeof module !== 'undefined' && module.exports) return 'node';
```

We have one check for now obsolete [PhantomJS](https://phantomjs.org/) 
browser automation software and another check for NodeJS environment. If any
of these fail the the main computation is not performed and correct result
is not achieved.

Another thing to pay attention to is the following two statements at the 
bottom of code:

```javascript
    document.cookie = "KEY=" + n + "*" + p / n + ":" + s + ":2460963898:1;path=/;";
    document.location.reload(true);
```

The first one sets the cookie based on initial hardcoded numbers and return 
value of `leastFactor()` function. Second one forces page reload, so that
web server could see the cookie and give the proper page instead of JS
challenge we got here.

So if we want to scrape the site we need to manufacture the cookie based on
JS challenge code we're getting without triggering checks for traces of 
automation. Is it trivial to pass the first check as PhantomJS is dead as of
2023. We could tamper with the code bit more and remove the check for NodeJS
modules, but this would entail a bit of cheating, as generally JS challenges are
obfuscated in more advanced way than what we see here.

Some options to create sandbox environment are:

* NodeJS `vm` API
* [`vm2`](https://github.com/patriksimek/vm2) module from NPM (recently discontinued)
* [`isolated-vm`](https://github.com/laverdet/isolated-vm) NPM module
* [JSDOM](https://github.com/jsdom/jsdom) - a lightweight emulator for
browser-like JS environment.
* Using an actual browser and controlling it programmatically.

We will keep it simple here and show a simple example based on the first option.
We save the challenge code into in.js. The following few lines of JS will read 
it and execute the challenge code in a sandbox environment to get the cookie:

```javascript
const fs = require("fs");
const vm = require("vm");

let js = fs.readFileSync("in.js", "utf-8");

const script = new vm.Script(js);
const mapperContext = { window: {}, document: {
  location: {
    reload: function(){}
  }
}};

const sandbox = vm.createContext(mapperContext);
script.runInContext(sandbox);
vm.runInContext('go();', sandbox);

console.log(sandbox.document.cookie);
```

We save this code into sandbox.js file.

Note that when creating a VM context (a sandbox) we provide an object called
`mapperContext` with some things that JS code expects to be there stubbed out.
For instance, to prevent the challenge code from crashing we provide an
empty implementation for `document.location.reload()` function. This ensures
that prerequisites for challenge code execution are met.

Next, there's `script.runInContext(sandbox);`. This statement "runs" the code
in VM, but since the original code contains only the two function declarations
without any call expression, we get it going in next line by calling `go()`
function in the sandbox environment. Lastly, we retrieve and print the
`document.cookie` value from the sandbox.

It turned out modifying the original code in any way was not necessary and
that it can be sandboxed as-is.

The following Bash script shows the entire steps to get the challenge, solve
it with sandboxing and using the cookie value to retrieve a proper page:

```bash
#!/bin/bash

set -x

curl "https://opencorporates.com" | \
    xmllint --html --xpath '//script/text()' - | \
    tail +2 > in.js # Deleting "<![CDATA[<!--" line

curl "https://opencorporates.com" -H "cookie: $(node sandbox.js)"
```

More advanced examples of JS sandboxing from and outside grayhat space are:

* [FlareSolverr](https://github.com/FlareSolverr/FlareSolverr) - a CloudFlare 
solver API server that relies on 
[undetected-chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver)
to solve CF challenges in modified browser environment.
* Google allows running some subset of JS language in Google Tag Manager
templates to enable further customisation. See the 
[Sandboxed JavaScript](https://developers.google.com/tag-platform/tag-manager/templates/sandboxed-javascript)
page.
