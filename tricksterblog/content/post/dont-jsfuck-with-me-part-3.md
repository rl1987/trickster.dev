+++
author = "rl1987"
title = "Don't JSFuck with me: Part 3"
draft = true
date = "2023-05-31"
tags = ["security", "reverse-engineering", "ast", "javascript"]
+++

Previously on Trickster Dev: [TODO: add links to parts 1 and 2]

By using AST transforms developed so far, JSFuck output for character `@` can 
be simplified to:

```javascript
[]["flat"]["constructor"]("return\"" + ([]["flat"]["constructor"]("return/false/")()["constructor"]("/") + [])[1] + [1] + [0] + [0] + "\"")();
```

What about other characters that have `null` value in the `MAPPING` object in
jsfuck.js? 

For `H` we have:

```javascript
[]["flat"]["constructor"]("return\"" + ([]["flat"]["constructor"]("return/false/")()["constructor"]("/") + [])[1] + [1] + [1] + [0] + "\"")();
```

For `J` we have:

```javascript
[]["flat"]["constructor"]("return\"" + ([]["flat"]["constructor"]("return/false/")()["constructor"]("/") + [])[1] + [1] + [1] + [2] + "\"")();
```

For `K` we have:

```javascript
[]["flat"]["constructor"]("return\"" + ([]["flat"]["constructor"]("return/false/")()["constructor"]("/") + [])[1] + [1] + [1] + [3] + "\"")();
```

For `~` we have:

```javascript
[]["flat"]["constructor"]("return\"" + ([]["flat"]["constructor"]("return/false/")()["constructor"]("/") + [])[1] + [1] + [7] + [6] + "\"")();
```

The code we end up is very similar and follows a clear pattern.

Again, we can use NodeJS REPL to verify that this crazy shebang evaluates back
to the original character:

```
> []["flat"]["constructor"]("return\"" + ([]["flat"]["constructor"]("return/false/")()["constructor"]("/") + [])[1] + [1] + [7] + [6] + "\"")();
'~'
```

Let us try to pick this stuff apart.

Due to type coercion, `[1] + [7] + [6]` part can be simplified to a single 
numeric string:

```
> [1] + [7] + [6]
'176'
```

Now what can we learn about code deeper in the statement?

```
> []["flat"]["constructor"]("return/false/")()
/false/
> []["flat"]["constructor"]("return/false/")()["constructor"]
[Function: RegExp]
> []["flat"]["constructor"]("return/false/")()["constructor"]("/")
/\//
> []["flat"]["constructor"]("return/false/")()["constructor"]("/") + []
'/\\//'
> ([]["flat"]["constructor"]("return/false/")()["constructor"]("/") + [])[1]
'\\'
```

This statement creates a regular expression object (`/false/`), accesses 
it's `contructor` property to get a corresponding constructor function object 
(`RegExp()`), calls it with parameter `/` (this results in new regular expression 
object), then add an empty array to a result to stringify it through type 
coercion. Resulting string is indexed to to extract a single backslash character.

Based on this, we can perform some manual simplifications to this code:

```
> []["flat"]["constructor"]("return\"" + ([]["flat"]["constructor"]("return/false/")()["constructor"]("/") + [])[1] + '176' + "\"")();
'~'
> []["flat"]["constructor"]("return\"" + (RegExp("/") + [])[1] + '176' + "\"")();
'~'
> []["flat"]["constructor"]("return\"" + '\\' + '176' + "\"")();
'~'
> []["flat"]["constructor"]("return\"\\176\"")();
'~'
```

What is the number 176 doing here? In the ASCII standard, octal 176 corresponds 
to character `~` (see ascii(7) manpage). After undoing this octal-encoding, code
gets even simpler:

```
> []["flat"]["constructor"]("return\"~\"")();
'~'
```

But what about this `[]["flat"]["constructor"]` part we have here? JSFuck web app
front page notes it is equivalent to calling `eval()`. Let us verify that for 
ourselves.

```
> []["flat"]
[Function: flat]
> typeof []["flat"]
'function'
> []["flat"]["constructor"]
[Function: Function]
> typeof []["flat"]["constructor"]
'function'
> []["flat"]["constructor"]("console.log(1)")
[Function: anonymous]
> []["flat"]["constructor"]("console.log(1)")()
1
undefined
> []["flat"]["constructor"] == Function
true
> Function("console.log(1)")()
1
undefined
```



