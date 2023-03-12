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

We can try using our [previously developed transform](https://github.com/rl1987/trickster.dev-code/blob/main/2023-02-24-dont-jsfuck-with-me-part-1/ast_transform.js) to simplify the code.

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

The above trick works by coercing `Array.prototype.flat()` to string (addition
operation prefers to convert stuff into strings) by adding `true` to it and
indexing the resulting string:

```
$ node
Welcome to Node.js v19.0.1.
Type ".help" for more information.
> []["flat"]
[Function: flat]
> String([]["flat"])
'function flat() { [native code] }'
> true + []["flat"]
'truefunction flat() { [native code] }'
> (true + []["flat"])[20]
'{'
```

So what we can do at AST level is pattern-match on `[]["flat"]` part, convert
it to string equivalent and replace it with equivalent `StringLiteral` node 
in the AST so that expression evaluation code can simplify it further. We
also should check if `[]["flat"]` is part of binary expression. This can be
done with a following transform:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "undo-flat-trick", // not required
    visitor: {
      MemberExpression(path) {
        let node = path.node;
        if (!t.isArrayExpression(node.object)) return;
        if (node.object.elements.length != 0) return;
        if (!t.isStringLiteral(node.property)) return;
        if (node.property.value === "flat" && t.isBinaryExpression(path.parent)) {
          path.replaceWith(t.stringLiteral(String(Array.prototype.flat)));
        }
      }
    }
  };
}
```

It converts the snippet we had to the following:

```javascript
(true + "function flat() { [native code] }")[20];
```

Our previous transform can pick it up from here, as we only have addition and
string indexing.

Similarly to the `flat()` trick, JSFuck abuses `entries()` method, as can
be seen in the following `MAPPING` object key-value pairs:

```javascript
    'b':   '([]["entries"]()+"")[2]',
    'j':   '([]["entries"]()+"")[3]',
    'A':   '(NaN+[]["entries"]())[11]',
    '[':   '([]["entries"]()+"")[0]',
    ']':   '([]["entries"]()+"")[22]',
```

The way to undo this is equivalent to dealing with `flat()` trick:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "undo-entries-trick", // not required
    visitor: {
      CallExpression(path) {
        let node = path.node;
        if (!t.isMemberExpression(node.callee)) return;
        if (!t.isArrayExpression(node.callee.object)) return;
        if (node.callee.object.elements.length != 0) return;
        if (!t.isStringLiteral(node.callee.property)) return;
        if (node.callee.property.value === "entries" && t.isBinaryExpression(path.parent)) {
          path.replaceWith(t.stringLiteral(String(Array.prototype.entries)));
        }
      }
    }
  };
}

```

Another thing that JSFuck does is abusing array's `concat()` method to obfuscate
a comma character:

```javascript
    ',':   '[[]]["concat"]([[]])+""',
```

This abuses how array string representation is computed, as evident by a quick
experiment in Node.JS REPL:

```
> [[]]["concat"]([[]])
[ [], [] ]
> String([[]]["concat"]([[]]))
','
> String([ [], [] ])
','
> [[]]["concat"]([[]]) + ""
','
```

Once again, we pattern-match the part that is to be converted to string due
to type coercion, create a `StringLiteral` out of it and replace it into
the AST:

```javascript
export default function (babel) {
  const { types: t } = babel;
  
  return {
    name: "undo-concat-trick", // not required
    visitor: {
      CallExpression(path) {
        let node = path.node;
        
        if (!t.isMemberExpression(node.callee)) return;
        if (!t.isArrayExpression(node.callee.object)) return;
        if (node.callee.object.elements.length != 1) return;
        if (!t.isArrayExpression(node.callee.object.elements[0])) return;
        if (node.callee.object.elements[0].elements.length != 0) return;
        
        if (!t.isStringLiteral(node.callee.property)) return;
        if (node.callee.property.value != "concat") return;
        
        if (!t.isArrayExpression(node.arguments[0])) return;
        if (node.arguments[0].elements.length != 1) return;
        if (!t.isArrayExpression(node.arguments[0].elements[0])) return;
        if (node.arguments[0].elements[0].elements.length != 0) return;
        
        if (!t.isBinaryExpression(path.parent)) return;
        
        path.replaceWith(t.valueToNode(String([ [], [] ])));
      }
    }
  };
}

```

In AST Explorer we can verify that `[[]]["concat"]([[]])+""` is converted to
`"," + "";`.

`String.prototype.slice()` method is also leveraged by JSFuck:

```
    'D':   'Function("return escape")()([]["flat"])["slice"]("-1")',
    '}':   '([]["flat"]+"")["slice"]("-1")',
```

We see that these cases also rely on some further trickery. Since we already
know how to deal with `flat()` trick, we will focus on the latter on for now.

Running the transform to undo `flat()` trick converts it to the following:

```javascript
("function flat() { [native code] }" + "")["slice"]("-1");
```

[According to the documentation](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/slice),
calling `slice()` on a string with single negative number returns a trailing 
substring. In this case it will be single-character substring, i.e. just the
last character.

We develop another AST transform to address the `slice()` trick:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "undo-slice-trick", // not required
    visitor: {
      CallExpression(path) {
        let node = path.node;
        if (!t.isMemberExpression(node.callee)) return;
        if (!t.isStringLiteral(node.callee.object)) return;
        if (!t.isStringLiteral(node.callee.property)) return;
        if (node.arguments.length != 1) return;
        if (node.callee.property.value === "slice" && 
            (t.isStringLiteral(node.arguments[0]) || 
             t.isNumericLiteral(node.arguments[0])) &&
             Number(node.arguments[0].value) === -1) {
          let fromStr = node.callee.object.value;
          path.replaceWith(t.valueToNode(fromStr.slice(-1)));
        }
      }
    }
  };
}

```

Nothing particulary different here, except that the subtree matching part
had to check for more things when matching. 

But before running this transform we have to deal with string concatenation,
as the matching is based on `StringLiteral` node being at `callee` property
of a `CallExpression`. Applying the 
[expression evaluation code](https://github.com/rl1987/trickster.dev-code/blob/main/2023-02-24-dont-jsfuck-with-me-part-1/ast_transform.js) simplifies
it to the form that is required by the new transform we just wrote:

```javascript
"function flat() { [native code] }"["slice"]("-1");
```

Now, when we apply the new transform we get the original character:

```javascript
"}";
```


