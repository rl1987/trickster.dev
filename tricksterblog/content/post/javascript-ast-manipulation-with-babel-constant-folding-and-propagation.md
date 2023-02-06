+++
author = "rl1987"
title = "JavaScript AST manipulation with Babel: constant folding and propagation"
date = "2023-02-07"
draft = true
tags = ["security", "reverse-engineering", "javascript"]
+++

Introducing constant recomputation is a commonly used code obfuscation
technique. Let's consider the following JavaScript snippet:

```javascript
const fourtyTwo = 42;
const msg = "The answer is:";
console.log(msg, fourtyTwo);
```

We have one numeric constant (`fourtyTwo`) and one string constant (`msg`)
that are passed into `console.log()`. Let us apply constant obfuscation by 
using [obfuscator.io](https://obfuscator.io) with "Numbers To Expressions"
and "Split Strings" checkboxes being on. 

[Screenshot 1](/2023-02-06_15.33.39.png)
[Screenshot 2](/2023-02-06_15.34.55.png)

This yields the following obfuscated version of the above snippet that we put 
into [AST Explorer](https://astexplorer.net):

```javascript
const fourtyTwo = 0x25fb + 0x3eb * -0x9 + -0x28e;
const msg = 'The\x20answer' + '\x20is:';
console['log'](msg, fourtyTwo);
```

[Screenshot 3](/2023-02-06_15.43.50.png)

Instead of simple integer constant and string we got some expressions that
can be evaluated back into the original values, thus retaining the original
behaviour of the code. 

In the Babel AST we have the following. Each variable assignment is represented
by `VariableDeclarator` object with stuff beyond the `=` sign at `init`
property. The `init` property points to a multi-level tree made up of mostly
`BinaryExpression` objects that represent a single arithmetic step (e.g.
adding two numbers or strings together). Number negation is represented
by `UnaryExpression` nodes. Leaves of this subtree are `NumericLiteral` and
`StringLiteral` nodes.

[Screenshot 4](/2023-02-06_15.44.54.png)
[Screenshot 5](/2023-02-06_15.44.23.png)
[Screenshot 6](/2023-02-06_15.44.54.png)

Turning numbers into hexadecimal form is also done as a minor obfuscation
that we can easily reverse. The trick is to delete `.extra.raw` in the
`NumericLiteral` objects affected by this obfuscation. To accomplish this, 
we write a quick AST transform in the AST Explorer tool:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "ast-transform", // not required
    visitor: {
      NumericLiteral(path) {
        if (path.node.extra.raw.startsWith("0x")) delete path.node.extra.raw;
      },
    }
  };
}

```

This cleans up the code a bit:

```javascript
const fourtyTwo = 9723 + 1003 * -9 + -654;
const msg = 'The\x20answer' + '\x20is:';
console['log'](msg, fourtyTwo);
```

[Screenshot 7](/2023-02-06_15.57.11.png)

After this sidenote, we now want to use Babel to turn these expressions
back into original values. This can be done by doing a code transformation 
known as constant folding. It is commonly performed by compilers during
code optimisation step. Since Babel is a bit like compiler, it can perform
it for us without the need of having to implement comprehensive JS expression 
handling algorithms or calling `eval()`. The key is to use `NodePath.evaluate()`
method in the visitor function. It returns a JavaScript result object with 
`confident` flag to let us know if it was able to evaluate the expression 
in a way that the result is conclusive (that is not always the case, as 
expressions can be more complicated than what we have here and involve 
variables that may change during runtime).

Once again, we can prototype our deobfuscation trick in AST Explorer. A 
simple example of constant folding would be like this:

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

We target `BinaryExpression` nodes with our visitor function and just call
the `evaluate()` method on associated `NodePath` object. If the result 
passes some simple sanity checks (the aforementioned `confident` flag, ability
to convert the resulting value into a `Literal`) we replace the 
`BinaryExpression` node with newly generated `NumericLiteral`/`StringLiteral`
node containing the same value that JS interpreter would have to compute.

The resulting deobfuscated code is as follows:

```javascript
const fourtyTwo = 42;
const msg = "The answer is:";
console['log'](msg, fourtyTwo);
```

[Screenshot 8](/2023-02-06_20.14.53.png)

So far, so good. But what if we wanted to take this a bit further? There's
really no need to have two named constants that are only used in `console.log()`
call, when we can just call it with the actual values. To replace references
to `msg` and `fourtyTwo` in the last statement we have to apply another 
code optimisation technique - constant propagation. Let me show a quick AST
transform to demonstrate it.

Let's put the following snippet into AST Explorer:

```javascript
const fourtyTwo = 42;
const msg = "The answer is:";
console.log(msg, fourtyTwo);

let t;
t = Math.floor(Date.now() / 1000);
console.log(t);
```

Since `t` here is not a constant it should be left unmodified.

Since code obfuscation solutions may introduce scope confusion by creating
multiple identifiers with same name in multiple lexical scopes, it's no
good to substitute variable names into values based on name alone. Luckily 
for us, we can use Babel scopes and bindings to perform substitution in a 
smarter way. The transform would be like this:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "ast-transform", // not required
    visitor: {
      VariableDeclarator(path) {
        if (path.node.init == null) return;
        if (!t.isLiteral(path.node.init)) return;
        const binding = path.scope.getBinding(path.node.id.name);
        if (!binding.constant) return;
        for (let i = 0; i < binding.referencePaths.length; i++) {
          let refPath = binding.referencePaths[i];
          refPath.replaceWith(path.node.init);
        }
        path.remove();
      } 
    }
  };
}

```

We target the `VariableDeclarator` nodes. In the visitor function we perform
some applicability checks. First we check if it declares a variable
with literal value by checking the `init` field. Next, we get a scope binding
object and check the `constant` Boolean property. If these checks pass, we
replace all the references to this variable with the literal node containing
the value. Lastly, we remove the constant declaration as we no longer need it
in the code. For more on scopes and bindings, see a previous post. [TODO: link]

The modified snippet is now the following:

```javascript
console.log("The answer is:", 42);
let t;
t = Math.floor(Date.now() / 1000);
console.log(t);

```

[Screenshot 9](/2023-02-06_16.55.59.png)

One last thing... In the above examples, a `const` keyword was used when 
declaring a constant, but it does not really matter for the purposes of this
kind of (de)obfuscation. All that matters is that a value is established once
and does not change later in the code.

