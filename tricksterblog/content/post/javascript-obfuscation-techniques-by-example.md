+++
author = "rl1987"
title = "Javascript obfuscation techniques by example"
date = "2022-07-10"
tags = ["security", "ast", "javascript", "scraping", "automation"]
+++

Sometimes when working on scraping some website you look into JavaScript code and it looks
like a complete mess that is impossible to read - no matter how much you squint, you cannot
make sense of it. That's because it has been obfuscated. Code obfuscation is a transformation
that is meant to make code difficult to read and reverse engineer. Many web sites utilize
JavaScript obfuscation to make things difficult to scraper/automation developers.

Consider the following very trivial Javascript statement:

```javascript
console.log("Hello, world! " + 123);
```

We will discuss various ways it can be obfuscated. To make things clear, we will go through
one obfuscation technique at a time and provide an example of how each technique changes this
code in a form that is meant to be unreadable. However, it should be noted that typically
multiple obfuscation methods are being utilized in scraping-resistant websites.

We will experiment with some online tools that obfuscate the JS code.

Hexadecimal string encoding
---------------------------

If we go to the uncreatively named [Javascript Obfuscator](https://javascriptobfuscator.com/Javascript-Obfuscator.aspx)
and switch off all checkboxes but "Encode Strings" the obfuscated code will look like this:

```javascript
console["\x6C\x6F\x67"]("\x48\x65\x6C\x6C\x6F\x2C\x20\x77\x6F\x72\x6C\x64\x21\x20"+ 123)
```

[Screenshot 1](/2022-07-09_16.19.07.png)

Each ASCII character of the hardcoded string was converted into hexadecimal form, as can be
verified with calculator in programmers mode. This is commonly done, but is pretty weak
way to hide stuff, as JavaScript REPL can be trivially used to reverse the transformation:

```
$ node
Welcome to Node.js v18.5.0.
Type ".help" for more information.
> "\x48\x65\x6C\x6C\x6F\x2C\x20\x77\x6F\x72\x6C\x64\x21\x20"
'Hello, world! '
> "\x6C\x6F\x67"
'log'
```

We can also notice that bracket notation is being used in the obfuscated form of the code -
`console.log` became `console["log"]`. That is also fairly common thing that JS obfuscation
solutions tend to do.

There's also another variation of this technique that involves replacing characters with their
unicode encoding.

String Array Mapping
--------------------

Now let us uncheck the "Encode Strings" checkbox and make the "Move Strings" checkbox on.
Clicking the Obfuscate button gives us the following code:

```javascript
var _0x8b75=["Hello, world! ","log"];console[_0x8b75[1]](_0x8b75[0]+ 123)
```

[Screenshot 2](/2022-07-09_16.31.59.png)

We can see that the code now has an array of strings that are being used indirectly
by referencing the array at various indices. 

Dead code injection
-------------------

Dead or unreachable code can be injected to make the Javascript source code larger and more
difficult to read without changing the functionality. Let us try it with 
[defendjs](https://github.com/alexhorn/defendjs):

```
$ defendjs --input hello.js --features dead_code --output .
```

This turns our trivial JS code into bit of a mess:

```javascript
(function () {
    function a(a, d) {
        var b = new Array(0);;
        var c = arguments;
        while (true)
            try {
                switch (a) {
                case 15229:
                    return;
                case 21176:
                    function e(a, b) {
                        return Array.prototype.slice.call(a).concat(Array.prototype.slice.call(b));
                    }
                    function f() {
                        var a = arguments[0], c = Array.prototype.slice.call(arguments, 1);
                        var b = function () {
                            return a.apply(this, c.concat(Array.prototype.slice.call(arguments)));
                        };
                        b.prototype = a.prototype;
                        return b;
                    }
                    function g(a, b) {
                        return Array.prototype.slice.call(a, b);
                    }
                    function h(b) {
                        var c = {};
                        for (var a = 0; a < b.length; a += 2) {
                            c[b[a]] = b[a + 1];
                        }
                        return c;
                    }
                    function i(a) {
                        return a.map(function (a) {
                            return String.fromCharCode(a & ~0 >>> 16) + String.fromCharCode(a >> 16);
                        }).join('');
                    }
                    function j() {
                        return String.fromCharCode.apply(null, arguments);
                    }
                    console.log('Hello, world! ' + 123);
                    a = 15229;
                    break;
                }
            } catch (b) {
                $$defendjs$tobethrown = null;
                switch (a) {
                default:
                    throw b;
                }
            }
    }
    a(21176, {});
}())
```

We can see our original statement, but it is nested pretty deep now. At the top level, there
is something called IIFE - Immediately Invoked Function Expression - a JS function that is
defined and called in a single statement. This function has two statements:

1. Declaration of function `a()` that takes two parameters.
2. Invocation of the function `a()` with first parameter value being 21176.

If we read the code of function `a()` we can see that the second parameter is ignored and 
that the only code path it can possibly take leads to `console.log()` statement with our 
message. Around that there's quite a bit of code that can never be executed - some functions
nested deep in a `switch` statement and also `try/catch` without any expections being possible.
Furthemore, it declares couple of variables in the beginning that will never be used because
the code will never take the paths where they are being accessed after being declared.

Scope obfuscation
-----------------

Let us rerun DefendJS with `scope` feature:

```
$ cp hello.js scope.js
$ defendjs --input scope.js --features scope --output .
```

This gives us the following code:

```javascript
(function () {
    {
        {
            function b(a, b) {
                return Array.prototype.slice.call(a).concat(Array.prototype.slice.call(b));
            }
            function c() {
                var a = arguments[0], c = Array.prototype.slice.call(arguments, 1);
                var b = function () {
                    return a.apply(this, c.concat(Array.prototype.slice.call(arguments)));
                };
                b.prototype = a.prototype;
                return b;
            }
            function d(a, b) {
                return Array.prototype.slice.call(a, b);
            }
            function e(b) {
                var c = {};
                for (var a = 0; a < b.length; a += 2) {
                    c[b[a]] = b[a + 1];
                }
                return c;
            }
            function f(a) {
                return a.map(function (a) {
                    return String.fromCharCode(a & ~0 >>> 16) + String.fromCharCode(a >> 16);
                }).join('');
            }
            function g() {
                return String.fromCharCode.apply(null, arguments);
            }
        }
        var a = [];
        console.log('Hello, world! ' + 123);
    }
}())
```

This technique may look like a simple version of previous one, but there's a key difference:
it introduces multiple lexical scopes with duplicate identifiers. For example, `a` might be
an argument to the first function in the innermost scope, or it can be a variable in the second
function, or even a variable in the same scope as our log statement. In our trivial example
it is easy to see through this as none of the functions in the innermost scope are called anywhere, 
but it's not going to be so simple in real world cases.

Control flow obfuscation
------------------------

Our dead code example also exemplifies a way that control flow can be made confusing - 
there a seemingly infinite loop that has try-catch structure inside it. Under `try`
there's a switch statement with two cases: one for returning out of the fuction, another
for calling the log function and setting the variable with a value that triggers the first
case with `return` statement. This introduces a confusing, roundabout codepath that is
functionally identical to our original single-line code.

Recomputation of literals
-------------------------

Let's try another feature of DefendsJS:

```
$ cp hello.js literals.js
$ defendjs --input literals.js --features literals --output .
```

The resulting code is:

```javascript
(function () {
    function c() {
        var c = arguments;
        var b = [];
        b[1] = '';
        b[1] += a(72);
        b[1] += a(101, 108, 108, 111);
        b[1] += a(44, 32, 119, 111);
        b[1] += a(114, 108, 100, 33);
        b[1] += a(32);
        return b[1];
    }
    {
        {
            function e(a, b) {
                return Array.prototype.slice.call(a).concat(Array.prototype.slice.call(b));
            }
            function d() {
                var a = arguments[0], c = Array.prototype.slice.call(arguments, 1);
                var b = function () {
                    return a.apply(this, c.concat(Array.prototype.slice.call(arguments)));
                };
                b.prototype = a.prototype;
                return b;
            }
            function f(a, b) {
                return Array.prototype.slice.call(a, b);
            }
            function g(b) {
                var c = {};
                for (var a = 0; a < b.length; a += 2) {
                    c[b[a]] = b[a + 1];
                }
                return c;
            }
            function h(a) {
                return a.map(function (a) {
                    return String.fromCharCode(a & ~0 >>> 16) + String.fromCharCode(a >> 16);
                }).join('');
            }
            function a() {
                return String.fromCharCode.apply(null, arguments);
            }
        }
        var b = [];
        console.log(d(c, b)() + 123);
    }
}())

```

In this case the hardcoded string is being recomputed in a confusing way so that it's far
from obvious from reading the code what it will be.

Mangling
--------

Mangling is a transformation that shortens variable and property names for optimization and obfuscation purposes.

Consider the following JS code:

```javascript
let oneTwoThree = 123;
let hello = "Hello, world! ";
console.log(hello + oneTwoThree);
```

Let's use mangling feature of DefendJS:

```
$ cp hello2.js mangling.js 
$ defendjs --input mangling.js --features mangle --output .
```

The resulting code is:

```javascript
(function () {
    var a = 123;
    var b = 'Hello, world! ';
    console.log(b + a);
}())
```

`oneTwoThree` became `a` and `hello` was renamed to `b`. This does not make a trivial example
that much harder to read, but could be one more thing that can be done to make big pieces of
JS difficult to understand, with the added benefit of making HTML pages containing inline JS lighter.
Developers tend to name their variables in a way that signify their meaning, which gets lost
when code is mangled.

Code minification
-----------------

This isn't much of obfuscation technique by itself, but minification - removing indentation, newlines
and whitespace from the code is often done as part of obfuscation process, in combination with
other techniques. 

JSFuck
------

[JSFuck](http://www.jsfuck.com/) is a way to convert JS code into esoteric style that resembles
the infamous Brainfuck programming language. `false` becomes `![]`, `true` becomes `!![]` and so on.

Converting our original JS code into JSFuck'ed version gives us the following:

```javascript
[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]][([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+[]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]]((!![]+[])[+!+[]]+(!![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+([][[]]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+!+[]]+(+[![]]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+!+[]]]+(!![]+[])[!+[]+!+[]+!+[]]+(+(!+[]+!+[]+!+[]+[+!+[]]))[(!![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([]+[])[([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+[]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]][([][[]]+[])[+!+[]]+(![]+[])[+!+[]]+((+[])[([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+[]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]]+[])[+!+[]+[+!+[]]]+(!![]+[])[!+[]+!+[]+!+[]]]](!+[]+!+[]+!+[]+[!+[]+!+[]])+(![]+[])[+!+[]]+(![]+[])[!+[]+!+[]])()([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]][([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+[]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]]((!![]+[])[+!+[]]+(!![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+([][[]]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+!+[]]+([]+[])[(![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(!![]+[])[+[]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]]()[+!+[]+[!+[]+!+[]]]+((!![]+[])[+[]]+[+!+[]]+[!+[]+!+[]+!+[]+!+[]]+[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+[+!+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]+!+[]+!+[]]+([][[]]+[])[+!+[]]+(![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+[+!+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]+!+[]+!+[]]+(![]+[])[!+[]+!+[]]+(!![]+[])[!+[]+!+[]+!+[]]+(+(+!+[]+[+!+[]]+(!![]+[])[!+[]+!+[]+!+[]]+[!+[]+!+[]]+[+[]])+[])[+!+[]]+(![]+[])[!+[]+!+[]]+(!![]+[])[+[]]+[+!+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]+!+[]+!+[]]+(!![]+[])[+[]]+[+!+[]]+[!+[]+!+[]+!+[]+!+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]+!+[]+!+[]]+(!![]+[])[+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]]+[+[]]+(!![]+[])[+[]]+[!+[]+!+[]+!+[]+!+[]]+[!+[]+!+[]]+(!![]+[])[+[]]+[+!+[]]+[+!+[]]+[+[]]+(!![]+[])[!+[]+!+[]+!+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[!+[]+!+[]]+(!![]+[])[+[]]+[+!+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]+!+[]+!+[]]+(!![]+[])[+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]]+[!+[]+!+[]+!+[]+!+[]]+(!![]+[])[+[]]+[!+[]+!+[]+!+[]+!+[]]+[+[]]+(!![]+[])[+[]]+[+!+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]+!+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]+!+[]+!+[]]+(!![]+[])[+[]]+[+!+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]+!+[]+!+[]]+(!![]+[])[+!+[]]+(![]+[])[!+[]+!+[]]+([][[]]+[])[!+[]+!+[]]+(!![]+[])[+[]]+[!+[]+!+[]+!+[]+!+[]]+[+!+[]]+(!![]+[])[+[]]+[!+[]+!+[]+!+[]+!+[]]+[+[]]+(!![]+[])[+[]]+[!+[]+!+[]+!+[]+!+[]]+[!+[]+!+[]]+(!![]+[])[+[]]+[!+[]+!+[]+!+[]+!+[]]+[+[]]+(!![]+[])[+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]]+[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+[!+[]+!+[]+!+[]+!+[]]+[+[]]+[+!+[]]+[!+[]+!+[]]+[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]]+[+!+[]]+(!![]+[])[+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]+!+[]+!+[]]+[!+[]+!+[]+!+[]])[(![]+[])[!+[]+!+[]+!+[]]+(+(!+[]+!+[]+[+!+[]]+[+!+[]]))[(!![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([]+[])[([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+[]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]][([][[]]+[])[+!+[]]+(![]+[])[+!+[]]+((+[])[([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+[]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]]+[])[+!+[]+[+!+[]]]+(!![]+[])[!+[]+!+[]+!+[]]]](!+[]+!+[]+!+[]+[+!+[]])[+!+[]]+(![]+[])[!+[]+!+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(!![]+[])[+[]]]((!![]+[])[+[]])[([][(!![]+[])[!+[]+!+[]+!+[]]+([][[]]+[])[+!+[]]+(!![]+[])[+[]]+(!![]+[])[+!+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(!![]+[])[!+[]+!+[]+!+[]]+(![]+[])[!+[]+!+[]+!+[]]]()+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([![]]+[][[]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]](([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]][([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+[]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]]((!![]+[])[+!+[]]+(!![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+([][[]]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+!+[]]+(![]+[+[]])[([![]]+[][[]])[+!+[]+[+[]]]+(!![]+[])[+[]]+(![]+[])[+!+[]]+(![]+[])[!+[]+!+[]]+([![]]+[][[]])[+!+[]+[+[]]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(![]+[])[!+[]+!+[]+!+[]]]()[+!+[]+[+[]]]+![]+(![]+[+[]])[([![]]+[][[]])[+!+[]+[+[]]]+(!![]+[])[+[]]+(![]+[])[+!+[]]+(![]+[])[!+[]+!+[]]+([![]]+[][[]])[+!+[]+[+[]]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(![]+[])[!+[]+!+[]+!+[]]]()[+!+[]+[+[]]])()[([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+[]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]]((![]+[+[]])[([![]]+[][[]])[+!+[]+[+[]]]+(!![]+[])[+[]]+(![]+[])[+!+[]]+(![]+[])[!+[]+!+[]]+([![]]+[][[]])[+!+[]+[+[]]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(![]+[])[!+[]+!+[]+!+[]]]()[+!+[]+[+[]]])+[])[+!+[]])+([]+[])[(![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(!![]+[])[+[]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]]()[+!+[]+[!+[]+!+[]]])())
```

[Screenshot 3](/2022-07-09_17.55.29.png)

Now, that's practically unreadable, but there's way to deobfuscate this kind of mess by performing
AST manipulation. 



