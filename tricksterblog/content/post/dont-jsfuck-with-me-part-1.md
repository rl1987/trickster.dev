+++
author = "rl1987"
title = "Don't JSFuck with me: Part 1"
date = "2023-02-24"
draft = true
tags = ["security", "reverse-engineering", "javascript"]
+++

Introduction
------------

[JSFuck](https://jsfuck.com) is a prominent JavaScript obfuscation tool that
converts JS code into a rather stangely looking form with only six characters:
`()+[]!`. For example, `console.log(1)` is turned into this:

```javascript
([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(![]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!![]+[])[!+[]+!+[]+!+[]]+(+(+!+[]+[+!+[]]+(!![]+[])[!+[]+!+[]+!+[]]+[!+[]+!+[]]+[+[]])+[])[+!+[]]+(![]+[])[!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(![]+[+[]]+([]+[])[([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+[]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]])[!+[]+!+[]+[+[]]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[+!+[]+[!+[]+!+[]+!+[]]]+[+!+[]]+([+[]]+![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[!+[]+!+[]+[+[]]]
```

[TODO: screenshot]

Code is made to be practically unreadable, but still retains it's
original functionality. What's the trick here? How can this possibly work?

Fortunately JSFuck is open source and we can take a look into the 
[source code](https://github.com/aemkei/jsfuck/blob/master/jsfuck.js). We
see that no AST level transformation are performed and that source code from
the user is being treated as a string. One thing it does is changing substrings
from the original source code into a weird form, such as:

* `false` becomes `![]`
* `true` becomes `!![]`
* Single `e` character becomes `(true+"")[3]`
* ... and so on.

If we copy-paste these weird expressions into JavaScript REPL they do indeed
get evaluated to their original form:

```
$ node
Welcome to Node.js v19.0.1.
Type ".help" for more information.
> ![]
false
> !![]
true
> (true+"")[3]
'e'
```

To understand what is going on here we must understand the concept of type
coercion. JavaScript is a weakly typed language, which means it provides
some leeway for developers using not exactly correct types. For example, `==`
operator allows us to compare between numeric string and actual number:

```
> "1" == 1
true
```

If we wanted to be more strict with the comparison here, we could use `===`
operator which also checks that both types are the same.

Type coercion is JavaScript language feature that entails applying type 
conversion implicity on as needed basis. For example, we may have a numeric
string that we may want to apply some math on. JS runtime would perform the 
type conversion for us:

```
> "100" / 3.14
31.84713375796178
```

However we must not rely too much on this, as sometimes the results may not
be what you would expect:

```
> "100" + 50
'10050'
```

Complete discussion of type coercion logic is outside the scope of this text,
but some big picture rules are the following:

* Addition operation prefers converting stuff to strings if one of the
sides is a string. Otherwise, it tries to convert it to numbers.
* Subtraction operation tries to convert operands to numbers before subtracting
them.
* There are truthy values that can be converted to `true` (this is most of all
values) and some falsy values that can be converted to `false` (`0`, `null`,
`undefined`, `NaN` and empty string). This applies when doing binary logic,
e.g. logical NOT operation (`![]` is false because empty array `[]` is truthy).
* Unary operations (single `+` or `-`) attempt conversion to numeric value.

For more on this, see the following pages on Mozilla developer portal:

* [Addition](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Addition)
* [Subtraction](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Subtraction)
* [Truthy](https://developer.mozilla.org/en-US/docs/Glossary/Truthy)
* [Falsy](https://developer.mozilla.org/en-US/docs/Glossary/Falsy)
* [Unary Plus](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Unary_plus)
* [Unary Negation](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Unary_negation)

So essentially what happens inside JSFuck is converting each character into
these weird JS expressions that evaluate it back to the original value by 
abusing JavaScript type coercion functionality. But not all characters 
can be conjured from empty data by applying basic computational operations. 
Sometimes JSFuck has to play tricks on implementation details of 
JavaScript engine to obfuscate stuff (more on this later).

Enhanced constant folding
-------------------------

WRITEME

... but this is not enough: further work
----------------------------------------

WRITEME
