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
converts JS code into a rather weird looking form with only six characters:
`()+[]!`. For example, `console.log(1)` is turned into this:

```javascript
([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(![]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!![]+[])[!+[]+!+[]+!+[]]+(+(+!+[]+[+!+[]]+(!![]+[])[!+[]+!+[]+!+[]]+[!+[]+!+[]]+[+[]])+[])[+!+[]]+(![]+[])[!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(![]+[+[]]+([]+[])[([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+[]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]])[!+[]+!+[]+[+[]]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[+!+[]+[!+[]+!+[]+!+[]]]+[+!+[]]+([+[]]+![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[!+[]+!+[]+[+[]]]
```

[Screenshot 1](/2023-02-24_17.33.21.png)

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

So we want to apply AST-level transformations on code obfuscated with JSFuck
to turn it back to it's original form (or something close enough). We have
previously tried applying 
[constant folding](/post/javascript-ast-manipulation-with-babel-constant-folding-and-propagation/)
for deobfuscation, so perhaps it can be used here as well? After all, we have
a lot of `BinaryExpression` and `UnaryExpression` nodes in the AST.

[Screenshot 2](/2023-02-24_17.37.58.png)

From the previous article we got the following code:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "ast-transform", // not required
    visitor: {
      BinaryExpression(path) {
        let evaluated = path.evaluate();
        if (!evaluated) return;
        if (!evaluated.confident) return;
        
        let value = evaluated.value;
        let valueNode = t.valueToNode(value);
        if (!t.isLiteral(valueNode)) return;
        
        path.replaceWith(valueNode);
      }
    }
  };
}
```

Let us try applying this on the obfuscated snippet in AST Explorer.

The code becomes:

```javascript
([]["false"[+[]] + "false"[2] + "false"[+!+[]] + "true"[+[]]] + [])[3] + (!![] + []["false"[+[]] + "false"[2] + "false"[+!+[]] + "true"[+[]]])["10"] + ([][[]] + [])[+!+[]] + "false"[3] + (!![] + []["false"[+[]] + "false"[2] + "false"[+!+[]] + "true"[+[]]])["10"] + "false"[2] + "true"[3] + (+("11" + "true"[3] + [2] + [+[]]) + [])[+!+[]] + "false"[2] + (!![] + []["false"[+[]] + "false"[2] + "false"[+!+[]] + "true"[+[]]])["10"] + ("false0" + ""[([]["false"[+[]] + "false"[2] + "false"[+!+[]] + "true"[+[]]] + [])[3] + (!![] + []["false"[+[]] + "false"[2] + "false"[+!+[]] + "true"[+[]]])["10"] + ([][[]] + [])[+!+[]] + "false"[3] + "true"[+[]] + "true"[+!+[]] + ([][[]] + [])[+[]] + ([]["false"[+[]] + "false"[2] + "false"[+!+[]] + "true"[+[]]] + [])[3] + "true"[+[]] + (!![] + []["false"[+[]] + "false"[2] + "false"[+!+[]] + "true"[+[]]])["10"] + "true"[+!+[]]])["20"] + ([]["false"[+[]] + "false"[2] + "false"[+!+[]] + "true"[+[]]] + [])["13"] + [+!+[]] + ("0false" + []["false"[+[]] + "false"[2] + "false"[+!+[]] + "true"[+[]]])["20"];
```

[Screenshot 3](/2023-02-24_17.48.38.png)

Re-applying the transform again does not simplify it any further. Clearly the 
AST transform code we have from before is not sufficient to undo JSFuck 
obfuscation. Let us see how it can be improved:

* We only target `BinaryExpression` nodes, but `UnaryExpression` nodes also
need be visited. The fix is simple: change `BinaryExpression(path)` to 
`"BinaryExpression|UnaryExpression"(path)`.
* JSFuck also abuses string indexing to pull out a character from larger string
(notice `"false"[2]`). Babel does not know how to simplify it without our help.
We need to target `MemberExpression` nodes to recognise when this is done 
and replace the entire `MemberExpression` with a `StringLiteral` containing
a resulting character.

More generally, we tried to make a leap and it didn't work out. Let's take
another look at JSFuck source code and re-approach it in smaller steps.

Consider the following mapping from the top of jsfuck.js:

```javascript
  const SIMPLE = {
    'false':      '![]',
    'true':       '!![]',
    'undefined':  '[][[]]',
    'NaN':        '+[![]]',
    'Infinity':   '+(+!+[]+(!+[]+[])[!+[]+!+[]+!+[]]+[+!+[]]+[+[]]+[+[]]+[+[]])' // +"1e1000"
  };
```

Let us try to deobfuscate the values in this objects back to the original form.

We fixed the node targeting, so `![]` is now converted back into `false` and
`!![]` is converted back into `true`.

However `[][[]]` is not simplified any further. That's because this is neither
binary not unary expression. It is empty array being indexed by empty array.

We can confirm in the JS REPL that this does resolve into `undefined`:

```
> [][[]]
undefined
```

Since at AST level this is `MemberExpression` with empty `ArrayExpression`s 
at `object` and `property` fields we can target a `MemberExpression` nodes
in our visitor, check bot fields for empty arrays and replace it with 
node representing value `undefined`. 

We add the following code to our AST transform:

```javascript
      MemberExpression(path) {
      	let node = path.node;
        if (t.isArrayExpression(node.object) &&
            node.object.elements.length == 0 &&
            t.isArrayExpression(node.property) &&
            node.property.elements.length == 0) {
          path.replaceWith(t.valueToNode(undefined));
        }
      }
```

Now we want `+[![]]` to be converted to `NaN`, but our current code only 
converts it to `+[false];`.

It might not be immediately obvious, but Babel does not generate `NumericLiteral`
node for `NaN` value when running `NodePath.evaluate()`/`valueWithNode()` 
on code like this. Instead, it generates a `BinaryExpression` representing 
division of zero by zero (`0 / 0`). Since we explicitly check if the value we
got is a literal it cannot proceed any further with this. But we also don't
want our code to run into infinite loop or bottomless recursion by trying to 
reduce an irreducible expression. So what we do is we replace the 
`BinaryExpression` with the result anyway, but if the result node is not 
a `NumericLiteral` we call `NodePath.skip()` to cut off traversal on the new 
node.

We modify constant folding code into the following:

```javascript
      "UnaryExpression|BinaryExpression"(path) {
        let result = path.evaluate();
        if (result.confident) {
          let valueNode = t.valueToNode(result.value);
          path.replaceWith(valueNode);
          if (!t.isLiteral(valueNode)) {
            path.skip();
          }
        }
      },
```

Now we got `0 / 0;` in the output, but we still want `NaN`. 

So we have to replace this binary expression with the appropriate node in the 
AST. We preempt the expression evaluation with the following code:

```javascript
        let node = path.node;
        
        if (t.isNumericLiteral(node.left) && t.isNumericLiteral(node.right) &&
           node.right.value === 0 && node.left.value === 0) {
          path.replaceWith(t.identifier('NaN'));
          return;
        }
```

Notice the early return here - it's needed so that code further in the transform
is not attempted, as we are overriding the Babel's `NodePath.evaluate()` stuff
and injecting our own answer. We don't want it to revert it back to `0 / 0` for
us.

So we got `NaN;` in the output now.

The following should be evaluated into `Infinity`:

```javascript
+(+!+[]+(!+[]+[])[!+[]+!+[]+!+[]]+[+!+[]]+[+[]]+[+[]]+[+[]])
```

Instead, the current transform turns it into:

```javascript
+(1 + "true"[3] + [1] + [0] + [0] + [0]);
```

We see something we did not address yet - string indexing operation. We further
improve our `MemberExpression` handling code to pull out the right character
for us and replace the `MemberExpression` with `StringLiteral`:

```javascript
        // https://stackoverflow.com/a/52986361/1044147
        function isNumeric(n) {
  	      return !isNaN(parseFloat(n)) && isFinite(n);
		}
          
        if (isNumeric(node.property.value)) {
          node.property = t.valueToNode(Number(node.property.value));
        }
        
      	if (t.isStringLiteral(node.object) && 
            t.isNumericLiteral(node.property)) {
      	  let character = node.object.value[node.property.value];
      	  path.replaceWith(t.valueToNode(character));
        }
```

Note that we also allow index to be a numeric string (I noticed this sometimes
happens in the intermediate results when I was experimenting).

Since we have more complex JS expression to deobfuscate, we now apply the
transform multiple times with the following results between steps:

1. `+(1 + "true"[3] + [1] + [0] + [0] + [0]);`
2. `+(1 + "e" + [1] + [0] + [0] + [0]);`
3. `1 / 0;`

The last expression cannot be simplified by the AST transform as it is, but
a fix is trivial with one more evaluation override that further improves what
we did in the `NaN` case:

```javascript
        if (t.isNumericLiteral(node.left) && t.isNumericLiteral(node.right)) {
          if (node.right.value === 0) {
           	if (node.left.value === 1) {
              path.replaceWith(t.identifier('Infinity'));
              return;
            } else if (node.left.value === 0) {
              path.replaceWith(t.identifier('NaN'));
              return;
            }
          }
        }
```

With this change, `1 / 0` is turned into `Infinity`.

Now let us try some obfuscated values from `MAPPING` object further down
below in jsfuck.js. `(false+"")[1]` should turn into `a`. Indeed our code
is able to deobfuscate it with `"false"[1];` as intermediate value. Likewise,
`(undefined+"")[2]` is turned into `"d";`.

At this point our AST transform is as follows:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "ast-transform", // not required
    visitor: {
      "UnaryExpression|BinaryExpression"(path) {
        let node = path.node;
        
        if (t.isNumericLiteral(node.left) && t.isNumericLiteral(node.right)) {
          if (node.right.value === 0) {
           	if (node.left.value === 1) {
              path.replaceWith(t.identifier('Infinity'));
              return;
            } else if (node.left.value === 0) {
              path.replaceWith(t.identifier('NaN'));
              return;
            }
          }
        }

        let result = path.evaluate();
        if (result.confident) {
          let valueNode = t.valueToNode(result.value);
          if (t.isLiteral(valueNode)) {
            path.replaceWith(valueNode);
          } else {
            path.replaceWith(valueNode);
            path.skip();
          }
        }
      },
      MemberExpression(path) {
      	let node = path.node;
        
        // https://stackoverflow.com/a/52986361/1044147
        function isNumeric(n) {
  	      return !isNaN(parseFloat(n)) && isFinite(n);
		}
          
        if (isNumeric(node.property.value)) {
          node.property = t.valueToNode(Number(node.property.value));
        }
        
      	if (t.isStringLiteral(node.object) && 
            t.isNumericLiteral(node.property)) {
      	  let character = node.object.value[node.property.value];
      	  path.replaceWith(t.valueToNode(character));
        }
        
        if (t.isArrayExpression(node.object) &&
            node.object.elements.length == 0 &&
            t.isArrayExpression(node.property) &&
            node.property.elements.length == 0) {
          path.replaceWith(t.valueToNode(undefined));
        }
      }
    }
  };
}

```

This is able to undo a lot of stuff that JSFuck is doing and works on great
fraction of `MAPPING` values.

... but this is not enough: further work
----------------------------------------

However, what about the `(true+[]["flat"])[20]` that should evaluate to a 
single `{` character? This one is not simplified any futher by our transform.

Let's unpack this expression in JS REPL:

```
> []["flat"]
[Function: flat]
> true + []["flat"]
'truefunction flat() { [native code] }'
> (true+[]["flat"])[20]
'{'
```

What we have here is that `[]["flat"]` gives us `flat()` function as object,
that is stringified by adding `true` to it and a character is extracted from
the resulting string. This kind of hack relies on JS runtime implementation
detail and our transform does not support this yet. It also does not support
the following:

```javascript
    '/':   '(false+[0])["italics"]()[10]',
    ':':   '(RegExp()+"")[3]',
    ';':   '("")["fontcolor"](NaN+")[21]',
    '<':   '("")["italics"]()[0]',
    '=':   '("")["fontcolor"]()[11]',
    '>':   '("")["italics"]()[2]',
    '?':   '(RegExp()+"")[2]',
```

To fully deobfuscate code from JSFuck we have to further improve our AST 
transform to cover all the weird hacks JSFuck is doing with JS functions.
That is the objective for the future work.

The plan is to have a trilogy of posts working towards complete reversal of
JSFuck'ed code. Second part will deal with JS function hacks. The third part
will be about tying up loose ends and developing a standalone deobfuscator
with some basic CLI.

