+++
author = "rl1987"
title = "Don't JSFuck with me: Part 2"
date = "2023-03-14"
draft = true
tags = ["security", "reverse-engineering", "ast", "javascript"]
+++

In the [previous post](/post/dont-jsfuck-with-me-part-1/) we went through using 
Babel AST transforms to simplify JSFuck-generated unary and binary expressions. 
This was shown to undo a lot, but not all of the obfuscation. What we still 
have to do is to deal with certain API and runtime hacks that JSFuck leverages 
to obfuscate some of the characters that are not covered just by abusing type
coercion and atomic components of JS (string and array indexing, logical/arithmetic 
operations).

Suppose we want to encode a `{` character with JSFuck. Putting this into 
[JSFuck web app](http://www.jsfuck.com) (make sure that checkboxes for additional 
features are not checked) yields the following code:

```javascript
(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[!+[]+!+[]+[+[]]]
```

[Screenshot 1](/2023-03-12_11.10.16.png)

If we put it into [ASTExplorer](https://astexplorer.net) we get pretty much
the same situation as before - a lot of `BinaryExpression`, `UnaryExpression`,
`ArrayExpression` and `MemberExpression` nodes making up the tree. 

[Screenshot 2](/2023-03-12_11.11.59.png)

We can try using our [previously developed transform](https://github.com/rl1987/trickster.dev-code/blob/main/2023-02-24-dont-jsfuck-with-me-part-1/ast_transform.js) to simplify the code.

Applying it three times gives us the following results:

1. `(true + []["false"[0] + "false"[2] + "false"[1] + "true"[0]])["20"];`
2. `(true + []["f" + "l" + "a" + "t"])[20];`
3. `(true + []["flat"])[20];`

The transform we have from earlier cannot simplify the code any further. What
we got here matches [line 108 in jsfuck.js](https://github.com/aemkei/jsfuck/blob/master/jsfuck.js#L108).

The above trick works by coercing `Array.prototype.flat()` to string by adding 
`true` to it (addition operation prefers to convert stuff into strings) and
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
had to check for some other things when matching. 

But before running this transform we have to deal with string concatenation,
as the matching is based on `StringLiteral` node being at `callee` property
of a `CallExpression`. Applying the 
[expression evaluation code](https://github.com/rl1987/trickster.dev-code/blob/main/2023-02-24-dont-jsfuck-with-me-part-1/ast_transform.js) simplifies
it to the form that is required by the new transform we just wrote:

```javascript
"function flat() { [native code] }"["slice"]("-1");
```

Now, when we apply the new transform we get the original character.

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

Besides `C` character this trick is also used to obfuscated `D` and `%` 
characters (in combination with some other tricks that we covered already):

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

JSFuck can also leverage `RegExp` API for obfuscation, as evident in the
following cases:

```javascript
    'E':   '(RegExp+"")[12]',
    'R':   '(+[]+RegExp)[10]',
    ':':   '(RegExp()+"")[3]',
    '?':   '(RegExp()+"")[2]',
    '\\':  '(RegExp("/")+"")[1]',
```

As you can see, in some cases `RegExp` identifier is used in addition operation 
but in other cases, a return value from `RegExp()` is used instead. We should 
cover both forms when deobfuscating.

These can be addressed with the following transform:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "undo-regexp-trick", // not required
    visitor: {
      Identifier(path) {
        let node = path.node;
       	if (!t.isBinaryExpression(path.parent)) return;
        if (path.parent.operator != "+") return;
        if (node.name === "RegExp") path.replaceWith(t.valueToNode(String(RegExp)));
      },
      CallExpression(path) {
        let node = path.node;
        if (!t.isBinaryExpression(path.parent)) return;
        if (path.parent.operator != "+") return;
        if (!t.isIdentifier(node.callee)) return;
        if (node.callee.name != "RegExp") return;
        if (node.arguments.length === 0) {
          path.replaceWith(t.valueToNode(String(RegExp())));
        } else if (node.arguments.length === 1 &&
                   t.isStringLiteral(node.arguments[0]) &&
                   node.arguments[0].value === "/") {
          path.replaceWith(t.valueToNode(String(RegExp("/"))));
        }
      }
    }
  };
}
```

There are few more string-based tricks that JSFuck does. One is by leveraging
the type name of `String` in the following cases:

```javascript
    'g':   '(false+[0]+String)[20]',
    'S':   '(+[]+String)[10]',
```

Getting these cases to the point of tractability by expression evaluation 
transform is easy and can be done with a transform very similar to the 
one for `Boolean` case earlier in this post:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "undo-string-trick", // not required
    visitor: {
      Identifier(path) {
        let node = path.node;
       	if (!t.isBinaryExpression(path.parent)) return;
        if (path.parent.operator != "+") return;
        if (node.name === "String") path.replaceWith(t.valueToNode(String(String)));
      }
    }
  };
}

```

Another trick we need to address is abusing `toString()` method as seen in
the following lines from jsfuck.js:

```javascript
    'h':   '(+(101))["to"+String["name"]](21)[1]',
    'k':   '(+(20))["to"+String["name"]](21)',
    'p':   '(+(211))["to"+String["name"]](31)[1]',
    'v':   '(+(31))["to"+String["name"]](32)',
    'w':   '(+(32))["to"+String["name"]](33)',
    'x':   '(+(101))["to"+String["name"]](34)[1]',
    'z':   '(+(35))["to"+String["name"]](36)',
    'U':   '(NaN+Object()["to"+String["name"]]["call"]())[11]',
```

With the exception of last case, all of these rely on calling
[`toString()` method](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/toString)
on a number to covert it to numeric string with non-standard base. In some
cases this numeric string is indexed to pull out the needed character.

Let us unpack the case for `h` in Node.JS REPL:

```
> (+(101))["to"+String["name"]](21)[1]
'h'
> String["name"]
'String'
> (+(101))
101
> "to"+String["name"]
'toString'
> 101["toString"](21)
'4h'
> 101["toString"](21)[1]
'h'
```

Applying the expression evaluation transform to the `h` case only simplifies 
the unary expression:

```javascript
101["to" + String["name"]](21)[1];
```

Before we proceed with number-to-string conversion here, let us write a
quick helper transform that simplifies `String["name"]` part:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "simplify-string-name", // not required
    visitor: {
      MemberExpression(path) {
        let node = path.node;
        if (!t.isIdentifier(node.object)) return;
        if (!t.isStringLiteral(node.property)) return;
        if (node.object.name === "String" && node.property.value === "name") {
          path.replaceWith(t.valueToNode("String"));
        }
      }
    }
  };
}
```

This simplifies the snippet to:

```javascript
101["to" + "String"](21)[1];
```

Applying expression evaluation transform on this simplifies it bit further:

```javascript
101["toString"](21)[1];
```

Once again, we pattern match on the relevant subtree and apply the change on it.

See the following transform:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "undo-number-tostring-trick", // not required
    visitor: {
      CallExpression(path) {
        let node = path.node;
        if (!t.isMemberExpression(node.callee)) return;
        if (!t.isNumericLiteral(node.callee.object)) return;
        if (!t.isStringLiteral(node.callee.property)) return;
        if (node.callee.property.value != "toString") return;
        if (node.arguments.length != 1) return;
        if (!t.isLiteral(node.arguments[0])) return;
        
        let numericStr = node.callee.object.value["toString"](node.arguments[0].value);
        path.replaceWith(t.valueToNode(numericStr));
      }
    }
  };
}
```

This turns our current snippet to:

```javascript
"4h"[1];
```

Now let us deal with the snippet for character `U`:

```javascript
(NaN+Object()["to"+String["name"]]["call"]())[11]
```

Applying our helper transform simplifies it to:

```javascript
(NaN + Object()["to" + "String"]["call"]())[11];
```

We can further simplify it by applying expression evaluation transform:

```javascript
(NaN + Object()["toString"]["call"]())[11];
```

Now we need another transform written that matches an exact subtree and
simplifies it further. It would look like this:

```javascript
export default function (babel) {
  const { types: t } = babel;
  
  return {
    name: "undo-object-tostring-call", // not required
    visitor: {
      CallExpression(path) {
        let node = path.node;
        let callee = node.callee;
        if (!t.isMemberExpression(callee)) return;
        let calleeObj = callee.object;
        if (!t.isMemberExpression(calleeObj)) return;
        if (!t.isCallExpression(calleeObj.object)) return;
        calleeObj = calleeObj.object;
        if (!t.isIdentifier(calleeObj.callee)) return;
        if (calleeObj.callee.name != "Object") return;
        if (!t.isStringLiteral(callee.property)) return;
        if (callee.property.value != "call") return;
        if (!t.isStringLiteral(callee.object.property)) return;
        if (callee.object.property.value != "toString") return;
        path.replaceWith(t.valueToNode(Object()["toString"]["call"]()));
      }
    }
  };
}
```

By applying this transform, we get the following snippet:

```javascript
(NaN + "[object Undefined]")[11];
```

This can be further simplified to character `U` by applying expression evaluation
transform two more times:

1. `"NaN[object Undefined]"[11];`
2. `"U";`

We're getting close to the end, but there's still some uncovered ground left. 
In the `MAPPING` object we see that some characters don't have matching 
snippet assignmed to them:

```javascript
    'H':   null,
    'J':   null,
    'K':   null,
    'L':   null,
    'P':   null,
    'Q':   null,
    'V':   null,
    'W':   null,
    'X':   null,
    'Y':   null,
    'Z':   null,
    '!':   null,
    '#':   null,
    '$':   null,
    '\'':  null,
    '*':   null,
    '@':   null,
    '^':   null,
    '_':   null,
    '`':   null,
    '|':   null,
    '~':   null
```

Let's try to find out what happens when one of these characters are being 
obfuscated. Can we deobfuscate them back? 

Obfuscating `@` with JSFuck gives us the following code:

```javascript
[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]][([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+[]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]]((!![]+[])[+!+[]]+(!![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+([][[]]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+!+[]]+([]+[])[(![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(!![]+[])[+[]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]]()[+!+[]+[!+[]+!+[]]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]][([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+[]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]]((!![]+[])[+!+[]]+(!![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+([][[]]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+!+[]]+(![]+[+[]])[([![]]+[][[]])[+!+[]+[+[]]]+(!![]+[])[+[]]+(![]+[])[+!+[]]+(![]+[])[!+[]+!+[]]+([![]]+[][[]])[+!+[]+[+[]]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(![]+[])[!+[]+!+[]+!+[]]]()[+!+[]+[+[]]]+![]+(![]+[+[]])[([![]]+[][[]])[+!+[]+[+[]]]+(!![]+[])[+[]]+(![]+[])[+!+[]]+(![]+[])[!+[]+!+[]]+([![]]+[][[]])[+!+[]+[+[]]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(![]+[])[!+[]+!+[]+!+[]]]()[+!+[]+[+[]]])()[([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+[]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]]((![]+[+[]])[([![]]+[][[]])[+!+[]+[+[]]]+(!![]+[])[+[]]+(![]+[])[+!+[]]+(![]+[])[!+[]+!+[]]+([![]]+[][[]])[+!+[]+[+[]]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(![]+[])[!+[]+!+[]+!+[]]]()[+!+[]+[+[]]])+[])[+!+[]]+[+!+[]]+[+[]]+[+[]]+([]+[])[(![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(!![]+[])[+[]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]]()[+!+[]+[!+[]+!+[]]])()
```

We put it into ASTExplorer and apply expression evaluation transform several
times:

1. `[]["false"[0] + "false"[2] + "false"[1] + "true"[0]][([]["false"[0] + "false"[2] + "false"[1] + "true"[0]] + [])[3] + (true + []["false"[0] + "false"[2] + "false"[1] + "true"[0]])["10"] + (undefined + [])[1] + "false"[3] + "true"[0] + "true"[1] + (undefined + [])[0] + ([]["false"[0] + "false"[2] + "false"[1] + "true"[0]] + [])[3] + "true"[0] + (true + []["false"[0] + "false"[2] + "false"[1] + "true"[0]])["10"] + "true"[1]]("true"[1] + "true"[3] + "true"[0] + (undefined + [])[0] + "true"[1] + (undefined + [])[1] + ""["false"[0] + (true + []["false"[0] + "false"[2] + "false"[1] + "true"[0]])["10"] + (undefined + [])[1] + "true"[0] + ([]["false"[0] + "false"[2] + "false"[1] + "true"[0]] + [])[3] + (true + []["false"[0] + "false"[2] + "false"[1] + "true"[0]])["10"] + "false"[2] + (true + []["false"[0] + "false"[2] + "false"[1] + "true"[0]])["10"] + "true"[1]]()["12"] + ([]["false"[0] + "false"[2] + "false"[1] + "true"[0]][([]["false"[0] + "false"[2] + "false"[1] + "true"[0]] + [])[3] + (true + []["false"[0] + "false"[2] + "false"[1] + "true"[0]])["10"] + (undefined + [])[1] + "false"[3] + "true"[0] + "true"[1] + (undefined + [])[0] + ([]["false"[0] + "false"[2] + "false"[1] + "true"[0]] + [])[3] + "true"[0] + (true + []["false"[0] + "false"[2] + "false"[1] + "true"[0]])["10"] + "true"[1]]("true"[1] + "true"[3] + "true"[0] + (undefined + [])[0] + "true"[1] + (undefined + [])[1] + "false0"[([false] + undefined)["10"] + "true"[0] + "false"[1] + "false"[2] + ([false] + undefined)["10"] + ([]["false"[0] + "false"[2] + "false"[1] + "true"[0]] + [])[3] + "false"[3]]()["10"] + false + "false0"[([false] + undefined)["10"] + "true"[0] + "false"[1] + "false"[2] + ([false] + undefined)["10"] + ([]["false"[0] + "false"[2] + "false"[1] + "true"[0]] + [])[3] + "false"[3]]()["10"])()[([]["false"[0] + "false"[2] + "false"[1] + "true"[0]] + [])[3] + (true + []["false"[0] + "false"[2] + "false"[1] + "true"[0]])["10"] + (undefined + [])[1] + "false"[3] + "true"[0] + "true"[1] + (undefined + [])[0] + ([]["false"[0] + "false"[2] + "false"[1] + "true"[0]] + [])[3] + "true"[0] + (true + []["false"[0] + "false"[2] + "false"[1] + "true"[0]])["10"] + "true"[1]]("false0"[([false] + undefined)["10"] + "true"[0] + "false"[1] + "false"[2] + ([false] + undefined)["10"] + ([]["false"[0] + "false"[2] + "false"[1] + "true"[0]] + [])[3] + "false"[3]]()["10"]) + [])[1] + [1] + [0] + [0] + ""["false"[0] + (true + []["false"[0] + "false"[2] + "false"[1] + "true"[0]])["10"] + (undefined + [])[1] + "true"[0] + ([]["false"[0] + "false"[2] + "false"[1] + "true"[0]] + [])[3] + (true + []["false"[0] + "false"[2] + "false"[1] + "true"[0]])["10"] + "false"[2] + (true + []["false"[0] + "false"[2] + "false"[1] + "true"[0]])["10"] + "true"[1]]()["12"])();`
2. `[]["f" + "l" + "a" + "t"][([]["f" + "l" + "a" + "t"] + [])[3] + (true + []["f" + "l" + "a" + "t"])[10] + "undefined"[1] + "s" + "t" + "r" + "undefined"[0] + ([]["f" + "l" + "a" + "t"] + [])[3] + "t" + (true + []["f" + "l" + "a" + "t"])[10] + "r"]("r" + "e" + "t" + "undefined"[0] + "r" + "undefined"[1] + ""["f" + (true + []["f" + "l" + "a" + "t"])[10] + "undefined"[1] + "t" + ([]["f" + "l" + "a" + "t"] + [])[3] + (true + []["f" + "l" + "a" + "t"])[10] + "l" + (true + []["f" + "l" + "a" + "t"])[10] + "r"]()[12] + ([]["f" + "l" + "a" + "t"][([]["f" + "l" + "a" + "t"] + [])[3] + (true + []["f" + "l" + "a" + "t"])[10] + "undefined"[1] + "s" + "t" + "r" + "undefined"[0] + ([]["f" + "l" + "a" + "t"] + [])[3] + "t" + (true + []["f" + "l" + "a" + "t"])[10] + "r"]("r" + "e" + "t" + "undefined"[0] + "r" + "undefined"[1] + "false0"["falseundefined"[10] + "t" + "a" + "l" + "falseundefined"[10] + ([]["f" + "l" + "a" + "t"] + [])[3] + "s"]()[10] + false + "false0"["falseundefined"[10] + "t" + "a" + "l" + "falseundefined"[10] + ([]["f" + "l" + "a" + "t"] + [])[3] + "s"]()[10])()[([]["f" + "l" + "a" + "t"] + [])[3] + (true + []["f" + "l" + "a" + "t"])[10] + "undefined"[1] + "s" + "t" + "r" + "undefined"[0] + ([]["f" + "l" + "a" + "t"] + [])[3] + "t" + (true + []["f" + "l" + "a" + "t"])[10] + "r"]("false0"["falseundefined"[10] + "t" + "a" + "l" + "falseundefined"[10] + ([]["f" + "l" + "a" + "t"] + [])[3] + "s"]()[10]) + [])[1] + [1] + [0] + [0] + ""["f" + (true + []["f" + "l" + "a" + "t"])[10] + "undefined"[1] + "t" + ([]["f" + "l" + "a" + "t"] + [])[3] + (true + []["f" + "l" + "a" + "t"])[10] + "l" + (true + []["f" + "l" + "a" + "t"])[10] + "r"]()[12])();`
3. `[]["flat"][([]["flat"] + [])[3] + (true + []["flat"])[10] + "n" + "s" + "t" + "r" + "u" + ([]["flat"] + [])[3] + "t" + (true + []["flat"])[10] + "r"]("ret" + "u" + "r" + "n" + ""["f" + (true + []["flat"])[10] + "n" + "t" + ([]["flat"] + [])[3] + (true + []["flat"])[10] + "l" + (true + []["flat"])[10] + "r"]()[12] + ([]["flat"][([]["flat"] + [])[3] + (true + []["flat"])[10] + "n" + "s" + "t" + "r" + "u" + ([]["flat"] + [])[3] + "t" + (true + []["flat"])[10] + "r"]("ret" + "u" + "r" + "n" + "false0"["i" + "t" + "a" + "l" + "i" + ([]["flat"] + [])[3] + "s"]()[10] + false + "false0"["i" + "t" + "a" + "l" + "i" + ([]["flat"] + [])[3] + "s"]()[10])()[([]["flat"] + [])[3] + (true + []["flat"])[10] + "n" + "s" + "t" + "r" + "u" + ([]["flat"] + [])[3] + "t" + (true + []["flat"])[10] + "r"]("false0"["i" + "t" + "a" + "l" + "i" + ([]["flat"] + [])[3] + "s"]()[10]) + [])[1] + [1] + [0] + [0] + ""["f" + (true + []["flat"])[10] + "n" + "t" + ([]["flat"] + [])[3] + (true + []["flat"])[10] + "l" + (true + []["flat"])[10] + "r"]()[12])();`
4. `[]["flat"][([]["flat"] + [])[3] + (true + []["flat"])[10] + "n" + "s" + "t" + "r" + "u" + ([]["flat"] + [])[3] + "t" + (true + []["flat"])[10] + "r"]("return" + ""["f" + (true + []["flat"])[10] + "n" + "t" + ([]["flat"] + [])[3] + (true + []["flat"])[10] + "l" + (true + []["flat"])[10] + "r"]()[12] + ([]["flat"][([]["flat"] + [])[3] + (true + []["flat"])[10] + "n" + "s" + "t" + "r" + "u" + ([]["flat"] + [])[3] + "t" + (true + []["flat"])[10] + "r"]("return" + "false0"["itali" + ([]["flat"] + [])[3] + "s"]()[10] + false + "false0"["itali" + ([]["flat"] + [])[3] + "s"]()[10])()[([]["flat"] + [])[3] + (true + []["flat"])[10] + "n" + "s" + "t" + "r" + "u" + ([]["flat"] + [])[3] + "t" + (true + []["flat"])[10] + "r"]("false0"["itali" + ([]["flat"] + [])[3] + "s"]()[10]) + [])[1] + [1] + [0] + [0] + ""["f" + (true + []["flat"])[10] + "n" + "t" + ([]["flat"] + [])[3] + (true + []["flat"])[10] + "l" + (true + []["flat"])[10] + "r"]()[12])();`

Now we apply `undo-flat-trick` transform:

5. `[]["flat"][("function flat() { [native code] }" + [])[3] + (true + "function flat() { [native code] }")[10] + "n" + "s" + "t" + "r" + "u" + ("function flat() { [native code] }" + [])[3] + "t" + (true + "function flat() { [native code] }")[10] + "r"]("return" + ""["f" + (true + "function flat() { [native code] }")[10] + "n" + "t" + ("function flat() { [native code] }" + [])[3] + (true + "function flat() { [native code] }")[10] + "l" + (true + "function flat() { [native code] }")[10] + "r"]()[12] + ([]["flat"][("function flat() { [native code] }" + [])[3] + (true + "function flat() { [native code] }")[10] + "n" + "s" + "t" + "r" + "u" + ("function flat() { [native code] }" + [])[3] + "t" + (true + "function flat() { [native code] }")[10] + "r"]("return" + "false0"["itali" + ("function flat() { [native code] }" + [])[3] + "s"]()[10] + false + "false0"["itali" + ("function flat() { [native code] }" + [])[3] + "s"]()[10])()[("function flat() { [native code] }" + [])[3] + (true + "function flat() { [native code] }")[10] + "n" + "s" + "t" + "r" + "u" + ("function flat() { [native code] }" + [])[3] + "t" + (true + "function flat() { [native code] }")[10] + "r"]("false0"["itali" + ("function flat() { [native code] }" + [])[3] + "s"]()[10]) + [])[1] + [1] + [0] + [0] + ""["f" + (true + "function flat() { [native code] }")[10] + "n" + "t" + ("function flat() { [native code] }" + [])[3] + (true + "function flat() { [native code] }")[10] + "l" + (true + "function flat() { [native code] }")[10] + "r"]()[12])();`

Continuing with expression evaluation:

6. `[]["flat"]["function flat() { [native code] }"[3] + "truefunction flat() { [native code] }"[10] + "n" + "s" + "t" + "r" + "u" + "function flat() { [native code] }"[3] + "t" + "truefunction flat() { [native code] }"[10] + "r"]("return" + ""["f" + "truefunction flat() { [native code] }"[10] + "n" + "t" + "function flat() { [native code] }"[3] + "truefunction flat() { [native code] }"[10] + "l" + "truefunction flat() { [native code] }"[10] + "r"]()[12] + ([]["flat"]["function flat() { [native code] }"[3] + "truefunction flat() { [native code] }"[10] + "n" + "s" + "t" + "r" + "u" + "function flat() { [native code] }"[3] + "t" + "truefunction flat() { [native code] }"[10] + "r"]("return" + "false0"["itali" + "function flat() { [native code] }"[3] + "s"]()[10] + false + "false0"["itali" + "function flat() { [native code] }"[3] + "s"]()[10])()["function flat() { [native code] }"[3] + "truefunction flat() { [native code] }"[10] + "n" + "s" + "t" + "r" + "u" + "function flat() { [native code] }"[3] + "t" + "truefunction flat() { [native code] }"[10] + "r"]("false0"["itali" + "function flat() { [native code] }"[3] + "s"]()[10]) + [])[1] + [1] + [0] + [0] + ""["f" + "truefunction flat() { [native code] }"[10] + "n" + "t" + "function flat() { [native code] }"[3] + "truefunction flat() { [native code] }"[10] + "l" + "truefunction flat() { [native code] }"[10] + "r"]()[12])();`
7. `[]["flat"]["c" + "o" + "n" + "s" + "t" + "r" + "u" + "c" + "t" + "o" + "r"]("return" + ""["f" + "o" + "n" + "t" + "c" + "o" + "l" + "o" + "r"]()[12] + ([]["flat"]["c" + "o" + "n" + "s" + "t" + "r" + "u" + "c" + "t" + "o" + "r"]("return" + "false0"["itali" + "c" + "s"]()[10] + false + "false0"["itali" + "c" + "s"]()[10])()["c" + "o" + "n" + "s" + "t" + "r" + "u" + "c" + "t" + "o" + "r"]("false0"["itali" + "c" + "s"]()[10]) + [])[1] + [1] + [0] + [0] + ""["f" + "o" + "n" + "t" + "c" + "o" + "l" + "o" + "r"]()[12])();`
8. `[]["flat"]["constructor"]("return" + ""["fontcolor"]()[12] + ([]["flat"]["constructor"]("return" + "false0"["italics"]()[10] + false + "false0"["italics"]()[10])()["constructor"]("false0"["italics"]()[10]) + [])[1] + [1] + [0] + [0] + ""["fontcolor"]()[12])();`

We see `fontcolor` in the code now, so let us apply `undo-fontcolor-trick`
transform:

9. `[]["flat"]["constructor"]("return" + "<font color=\"undefined\"></font>"[12] + ([]["flat"]["constructor"]("return" + "false0"["italics"]()[10] + false + "false0"["italics"]()[10])()["constructor"]("false0"["italics"]()[10]) + [])[1] + [1] + [0] + [0] + "<font color=\"undefined\"></font>"[12])();`

We can also see that `undo-italics-trick` transform is applicable, so let us apply
that as well:

10. `[]["flat"]["constructor"]("return" + "<font color=\"undefined\"></font>"[12] + ([]["flat"]["constructor"]("return" + "<i>false0</i>"[10] + false + "<i>false0</i>"[10])()["constructor"]("<i>false0</i>"[10]) + [])[1] + [1] + [0] + [0] + "<font color=\"undefined\"></font>"[12])();`

Further simplifications with expression evaluation transform:

11. `[]["flat"]["constructor"]("return" + "\"" + ([]["flat"]["constructor"]("return" + "/" + false + "/")()["constructor"]("/") + [])[1] + [1] + [0] + [0] + "\"")();`
12. `[]["flat"]["constructor"]("return\"" + ([]["flat"]["constructor"]("return/false/")()["constructor"]("/") + [])[1] + [1] + [0] + [0] + "\"")();`

Now, what the fuck is this? We can verify that this stuff does indeed evaluate
back to the original character:

```
> []["flat"]["constructor"]("return\"" + ([]["flat"]["constructor"]("return/false/")()["constructor"]("/") + [])[1] + [1] + [0] + [0] + "\"")();
'@'
```

It also seems to be related to `eval()` function, as we see the following
in jsfuck.js:

```javascript
    if (wrapWithEval){
      if (runInParentScope){
        output = "[][" + encode("flat") + "]" +
          "[" + encode("constructor") + "]" +
          "(" + encode("return eval") + ")()" +
          "(" + output + ")";
      } else {
        output = "[][" + encode("flat") + "]" +
          "[" + encode("constructor") + "]" +
          "(" + output + ")()";
      }
    }
```

However completely untangling this at AST level is a matter of future research
that I will hopefully finish in the upcoming weeks. Researching how to undo 
JSFuck obfuscation has been fun and interesting, but there are other
priorities now.

To be continued...
