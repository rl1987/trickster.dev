+++
author = "rl1987"
title = "Don't JSFuck with me: Part 2"
date = "2023-03-15"
draft = true
tags = ["security", "reverse-engineering", "ast", "javascript"]
+++

In the [previous post](/post/dont-jsfuck-with-me-part-1/) we went through using 
Babel AST transforms to simplify JSFuck-generated unary and binary expressions. 
This was shown to undo a lot, but not all of the obfuscation. What we still 
have to do is to deal with certain API and runtime hacks that JSFuck leverages 
to obfuscate some of the characters that are not covered just by abusing type
coercion and atomic components of JS (string indexing, logical/arithmetic 
operations).

Suppose we want to encode a `{` character with JSFuck. Putting this into 
[JSFuck web app](http://www.jsfuck.com) (make sure that checkboxes for additional 
features are not checked) yields the following code:

```javascript
(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[!+[]+!+[]+[+[]]]
```

If we put it into [ASTExplorer](https://astexplorer.net) we get pretty much
the same situation as before - a lot of `BinaryExpression`, `UnaryExpression`,
`ArrayExpression` and `MemberExpression` nodes making up the tree. 

We can try using our previously developed transform to simplify the code.

First run of the transform gives us:

```javascript
(true + []["false"[0] + "false"[2] + "false"[1] + "true"[0]])["20"];
```

Second run gives us:

```javascript
(true + []["f" + "l" + "a" + "t"])[20];
```

Third run yields the following:

```javascript
(true + []["flat"])[20];
```

The transform we have from earlier cannot simplify the code any further. What
we got here matches [line 108 in jsfuck.js](https://github.com/aemkei/jsfuck/blob/master/jsfuck.js#L108).

