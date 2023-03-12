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

Letter `B` is obfuscated by leveraging `Boolean` type name:

```javascript
    'B':   '(+[]+Boolean)[10]',
```

Running the expression evaluation code on the obfuscated snippet converts it to:

```javascript
(0 + Boolean)[10];
```

Now we can undo the `Boolean` trick, which is quite trivial:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "undo-boolean-trick", // not required
    visitor: {
      Identifier(path) {
        let node = path.node;
       	if (!t.isBinaryExpression(path.parent)) return;
        if (path.parent.operator != "+") return;
        if (node.name === "Boolean") path.replaceWith(t.valueToNode(String(Boolean)));
      }
    }
  };
}
```

Running this one gives us the following snippet:

```javascript
(0 + "function Boolean() { [native code] }")[10];
```

Running expression evaluation transform twice simplifies this to `B` character:

1. `"0function Boolean() { [native code] }"[10];`
2. `"B";`

JSFuck also abuses a `fontcolor()` function to encode some characters:

```javascript
    'q':   '("")["fontcolor"]([0]+false+")[20]',
    '"':   '("")["fontcolor"]()[12]',
    '&':   '("")["fontcolor"](")[13]',
    ';':   '("")["fontcolor"](NaN+")[21]',
    '=':   '("")["fontcolor"]()[11]',
```

This trick actually relies on the output of `fontcolor()` function:

```
> ("")["fontcolor"]()[11]
'='
> ("")["fontcolor"]()
'<font color="undefined"></font>'
> String.prototype.fontcolor("")
'<font color=""></font>'
> String.prototype.fontcolor()[11]
'='
```

AST transform to undo this would be as follows:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "undo-fontcolor-trick", // not required
    visitor: {
      CallExpression(path) {
        let node = path.node;
        if (!t.isMemberExpression(node.callee)) return;
        if (!t.isStringLiteral(node.callee.object)) return;
        if (!t.isStringLiteral(node.callee.property)) return;
        if (node.callee.property.value === "fontcolor") {
           if (node.arguments.length === 0) {
             path.replaceWith(t.valueToNode(String.prototype.fontcolor()));
           } else if (t.isLiteral(node.arguments[0])) {
             path.replaceWith(t.valueToNode(String.prototype.fontcolor(node.arguments[0].value)))
           }
        }
      }
    }
  };
}
```

`("")["fontcolor"]()[12]` (snippet for double-quote character) is simplified
to `"<font color=\"undefined\"></font>"[12];`.

Let's go through a somewhat bigger example.

Obfuscating a semicolon character yields the following code:

```javascript
([]+[])[(![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(!![]+[])[+[]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]](+[![]]+([]+[])[(![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(!![]+[])[+[]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]]()[+!+[]+[!+[]+!+[]]])[!+[]+!+[]+[+!+[]]]
```

We can apply the expression evaluation transform until we hit the `flat()` trick:

1. `""["false"[0] + (true + []["false"[0] + "false"[2] + "false"[1] + "true"[0]])["10"] + (undefined + [])[1] + "true"[0] + ([]["false"[0] + "false"[2] + "false"[1] + "true"[0]] + [])[3] + (true + []["false"[0] + "false"[2] + "false"[1] + "true"[0]])["10"] + "false"[2] + (true + []["false"[0] + "false"[2] + "false"[1] + "true"[0]])["10"] + "true"[1]](0 / 0 + ""["false"[0] + (true + []["false"[0] + "false"[2] + "false"[1] + "true"[0]])["10"] + (undefined + [])[1] + "true"[0] + ([]["false"[0] + "false"[2] + "false"[1] + "true"[0]] + [])[3] + (true + []["false"[0] + "false"[2] + "false"[1] + "true"[0]])["10"] + "false"[2] + (true + []["false"[0] + "false"[2] + "false"[1] + "true"[0]])["10"] + "true"[1]]()["12"])["21"];`
2. `""["f" + (true + []["f" + "l" + "a" + "t"])[10] + "undefined"[1] + "t" + ([]["f" + "l" + "a" + "t"] + [])[3] + (true + []["f" + "l" + "a" + "t"])[10] + "l" + (true + []["f" + "l" + "a" + "t"])[10] + "r"](NaN + ""["f" + (true + []["f" + "l" + "a" + "t"])[10] + "undefined"[1] + "t" + ([]["f" + "l" + "a" + "t"] + [])[3] + (true + []["f" + "l" + "a" + "t"])[10] + "l" + (true + []["f" + "l" + "a" + "t"])[10] + "r"]()[12])[21];`
3. `""["f" + (true + []["flat"])[10] + "n" + "t" + ([]["flat"] + [])[3] + (true + []["flat"])[10] + "l" + (true + []["flat"])[10] + "r"](NaN + ""["f" + (true + []["flat"])[10] + "n" + "t" + ([]["flat"] + [])[3] + (true + []["flat"])[10] + "l" + (true + []["flat"])[10] + "r"]()[12])[21];`

Applying the previous transform to undo this provides us with path to further
apply expression evaluation:

4. `""["f" + (true + "function flat() { [native code] }")[10] + "n" + "t" + ("function flat() { [native code] }" + [])[3] + (true + "function flat() { [native code] }")[10] + "l" + (true + "function flat() { [native code] }")[10] + "r"](NaN + ""["f" + (true + "function flat() { [native code] }")[10] + "n" + "t" + ("function flat() { [native code] }" + [])[3] + (true + "function flat() { [native code] }")[10] + "l" + (true + "function flat() { [native code] }")[10] + "r"]()[12])[21];`
5. `""["f" + "truefunction flat() { [native code] }"[10] + "n" + "t" + "function flat() { [native code] }"[3] + "truefunction flat() { [native code] }"[10] + "l" + "truefunction flat() { [native code] }"[10] + "r"](NaN + ""["f" + "truefunction flat() { [native code] }"[10] + "n" + "t" + "function flat() { [native code] }"[3] + "truefunction flat() { [native code] }"[10] + "l" + "truefunction flat() { [native code] }"[10] + "r"]()[12])[21];`
6. `""["f" + "o" + "n" + "t" + "c" + "o" + "l" + "o" + "r"](NaN + ""["f" + "o" + "n" + "t" + "c" + "o" + "l" + "o" + "r"]()[12])[21];`
7. `""["fontcolor"](NaN + ""["fontcolor"]()[12])[21];`

Now it's time to apply the `undo-fontcolor-trick` transform:

8. `""["fontcolor"](NaN + "<font color=\"undefined\"></font>"[12])[21];`

We do two more iterations of expression evaluation:

9. `""["fontcolor"](NaN + "\"")[21];`
10. `""["fontcolor"]("NaN\"")[21];`

... and apply `undo-fontcolor-trick` transform once again:

10. `"<font color=\"NaN&quot;\"></font>"[21];`

Applying expression evaluation one more time gives us the original character:

11. `";";`

JSFuck abuses `italics()` in a similar way that is also based on indexing the
output string:

```javascript
    '/':   '(false+[0])["italics"]()[10]',
    '<':   '("")["italics"]()[0]',
    '>':   '("")["italics"]()[2]',
    'C':   'Function("return escape")()(("")["italics"]())[2]',
```

The transform to undo the trick is similar to the one we did for `fontcolor()`
case:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "undo-italics-trick", // not required
    visitor: {
      CallExpression(path) {
        let node = path.node;
        if (!t.isMemberExpression(node.callee)) return;
        if (!t.isStringLiteral(node.callee.object)) return;
        if (!t.isStringLiteral(node.callee.property)) return;
        if (node.callee.property.value === "italics") {
           const fromStr = node.callee.object.value;
           if (node.arguments.length === 0) {
             path.replaceWith(t.valueToNode(fromStr.italics()));
           } 
        }
      }
    }
  };
}
```

Quick check on AST Explorer shows that `("")["italics"]()[0]` is simplified to
`"<i></i>"[0];`, which is something we can process further with the other code.

When encoding character `C`, JSFuck also does another trick that relies on
using `escape()` function to URL-encode some string, then indexing the output:

```
> Function("return escape")()(("")["italics"]())[2]
'C'
> Function("return escape")()(("")["italics"]())
'%3Ci%3E%3C/i%3E'
> ("")["italics"]()
'<i></i>'
> Function("return escape")()('<i></i>')
'%3Ci%3E%3C/i%3E'
> Function("return escape")()('<i></i>')[2]
'C'
> escape('<i></i>')
'%3Ci%3E%3C/i%3E'
> escape('<i></i>')[2]
'C'
```

Besides `C` character this trick is used to obfuscated `D` and `%` characters
(in combination with some other tricks that we covered already):

```javascript
    'C':   'Function("return escape")()(("")["italics"]())[2]',
    'D':   'Function("return escape")()([]["flat"])["slice"]("-1")',
    '%':   'Function("return escape")()([]["flat"])[21]',
```

Applying the `undo-italics-trick` to the snippet from the first case turns
it into:

```javascript
Function("return escape")()("<i></i>")[2];
```

Now we need an AST transform that calls `escape()` function and substitutes
a URL-encoded string into the AST. We also need to deal with a special case
of the `flat()` trick. The previous transform will not work as-is due to being
developed for cases with binary expressions.

So the AST transform to deal with this stuff would be like this:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "undo-function-escape-trick", // not required
    visitor: {
      MemberExpression(path) {
        let node = path.node;
        if (!t.isArrayExpression(node.object)) return;
        if (node.object.elements.length != 0) return;
        if (!t.isStringLiteral(node.property)) return;
        if (node.property.value === "flat") path.replaceWith(t.valueToNode(String(Array.prototype.flat)));
      },
      CallExpression(path) {
        let node = path.node;
        if (t.isCallExpression(node.callee) &&
            t.isCallExpression(node.callee.callee) &&
            t.isIdentifier(node.callee.callee.callee) &&
            node.callee.callee.callee.name === "Function" &&
            node.callee.callee.arguments.length === 1 &&
            t.isStringLiteral(node.callee.callee.arguments[0]) &&
            node.callee.callee.arguments[0].value === "return escape" &&
            t.isStringLiteral(node.arguments[0])
           ) {
            path.replaceWith(t.valueToNode(escape(node.arguments[0].value)));
        }
      }
    }
  };
}
```

Let us try it on the snippet for `%` character - `Function("return escape")()([]["flat"])[21]`.
We need to do it twice.

1. `Function("return escape")()("function flat() { [native code] }")[21];`
2. `"function%20flat%28%29%20%7B%20%5Bnative%20code%5D%20%7D"[21];`

Expression evaluation transform pulls out the `%` character from this.

For 3 of the characters, JSFuck relies on calling `Date()` to obfuscate them:

```javascript
    'G':   '(false+Function("return Date")()())[30]',
    'M':   '(true+Function("return Date")()())[30]',
    'T':   '(NaN+Function("return Date")()())[30]',
```

This relies on characters `G`, `M` and `T` being always present in the output
of `Date()` function at predictable indices. Some dummy values are added to 
tweak the output string a little, then indexing it to pull out the needed 
character.

The transform code to undo this is similar to the ones we wrote before:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "undo-function-date-trick", // not required
    visitor: {
      CallExpression(path) {
        let node = path.node;
        if (t.isCallExpression(node.callee) &&
            t.isCallExpression(node.callee.callee) &&
            t.isIdentifier(node.callee.callee.callee) &&
            node.callee.callee.callee.name === "Function" &&
            node.callee.callee.arguments.length === 1 &&
            t.isStringLiteral(node.callee.callee.arguments[0]) &&
            node.callee.callee.arguments[0].value === "return Date"
           ) {
            path.replaceWith(t.valueToNode(Date()));
        }
      }
    }
  };
}
```

This converts `Function("return Date")()()` (equivalent to `Date()`) part to
string literal with datetime string, which can be further dealt with by
the expression evaluation transform.


