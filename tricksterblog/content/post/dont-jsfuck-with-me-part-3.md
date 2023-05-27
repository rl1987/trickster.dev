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

So let us try to refactor this code bit by bit using Babel AST transformations.

First transformation is for converting `[]["flat"]["constructor"]("return/false/")()`
into `/false/`:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "simplify-false-regex", // not required
    visitor: {
      CallExpression(path) {
		const callExpr = path.node;
        if (callExpr.arguments.length != 0) return;
        if (!t.isCallExpression(callExpr.callee)) return;
        const calleeMemberExpr = callExpr.callee.callee;
        if (!t.isMemberExpression(calleeMemberExpr)) return;
        const memberExpr2 = calleeMemberExpr.object;
        if (!t.isMemberExpression(memberExpr2)) return;
        const arrayObj = memberExpr2.object;
        if (!t.isArrayExpression(arrayObj)) return;
        if (arrayObj.elements.length != 0) return;
        const property1 = memberExpr2.property;
        if (!t.isStringLiteral(property1)) return;
        if (property1.value != "flat") return;
        const property2 = calleeMemberExpr.property;
        if (!t.isStringLiteral(property2)) return;
        if (property2.value != "constructor") return;
        if (callExpr.callee.arguments.length != 1) return;
        const argStrLiteral = callExpr.callee.arguments[0];
        if (!t.isStringLiteral(argStrLiteral)) return;
        if (argStrLiteral.value != "return/false/") return;      
        path.replaceWith(t.regExpLiteral('false', ''));
      }
    }
  };
}
```

Now we need to deal with regexp constructor thing that accepts a string argument.
There's another transform for that:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "refactor-regex-constr", // not required
    visitor: {
      CallExpression(path) {
        const callExpr = path.node;
        if (callExpr.arguments.length != 1) return;
        const argument = callExpr.arguments[0];
        if (!t.isStringLiteral(argument)) return;
        const calleeMemberExpr = callExpr.callee;
        if (!t.isMemberExpression(calleeMemberExpr)) return;
        if (!t.isRegExpLiteral(calleeMemberExpr.object)) return;
        let property = calleeMemberExpr.property;
        if (!t.isStringLiteral(property)) return;
        if (property.value != "constructor") return;
        
        path.replaceWith(
          t.regExpLiteral(argument.value.replace('/', '\\/'), '')
        );
      }
    }
  };
}
```

Now we deal with addition of regular expression with empty array to stringify
the regular expression object. Current code from part 1 deals with similar
stuff, but is unable to cover what we have now. Thus we write one more
small transformation to only cover this case:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "regex-str", // not required
    visitor: {
      BinaryExpression(path) {
        const binExpr = path.node;
        const left = binExpr.left;
        if (!t.isRegExpLiteral(left)) return;
        const right = binExpr.right;
        if (!t.isArrayExpression(right)) return;
        if (right.elements.length != 0) return;
        
        const regexStr = String(RegExp(left.pattern));
        
        path.replaceWith(t.stringLiteral(regexStr));
      }
    }
  };
}
```

To convert `[]["flat"]["constructor"]()` into `eval()` calls we develop the
following transform:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "fix-eval", // not required
    visitor: {
      CallExpression(path) {
        let node = path.node;
        if (node.arguments.length != 1) return;
        if (!t.isStringLiteral(node.arguments[0])) return;
        let parent = path.parent;
        if (!t.isCallExpression(parent)) return;
        let callee = node.callee;
        if (!t.isMemberExpression(callee)) return;
        if (!t.isStringLiteral(callee.property)) return;
        let key1 = callee.property.value;
        if (!t.isMemberExpression(callee.object)) return;
        if (!t.isStringLiteral(callee.object.property)) return;
        let key2 = callee.object.property.value;
        if (key1 === "constructor" && (key2 === "filter" || key2 === "flat")) {
          let evalCallExpr = t.callExpression(t.identifier('eval'), node.arguments);
          path.parentPath.replaceWith(evalCallExpr);
        }
      }
    }
  };
}
```

To convert string-returning `eval()` calls into string literals we do one more
transformation:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "eval-return-str", // not required
    visitor: {
      CallExpression(path) {
        let node = path.node;
        if (!t.isIdentifier(node.callee)) return;
        if (node.callee.name != "eval") return;
        if (node.arguments.length != 1) return;
        if (!t.isStringLiteral(node.arguments[0])) return;
        
        let argStr = node.arguments[0].value;
        
        if (argStr.startsWith("return\"") && argStr.endsWith("\"")) {
          argStr = argStr.substr("return\"".length);
          argStr = argStr.substr(0, argStr.length-1);
          path.replaceWith(t.stringLiteral(argStr));
        }
      }
    }
  };
}
```

