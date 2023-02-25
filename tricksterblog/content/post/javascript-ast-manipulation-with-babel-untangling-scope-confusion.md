+++
author = "rl1987"
title = "JavaScript AST manipulation with Babel: untangling scope confusion"
date = "2023-01-25"
tags = ["security", "reverse-engineering", "ast", "javascript"]
+++

In computer programming, a lexical scope of an identifier (name of function, 
class, variable, constant, etc.) is area within the code where that identifier
can be used. Some identifiers have global scope meaning they can be used in the
entire program. Others have narrowed-down scope that is limited to one single
function or code block between curly braces. Identifier names can be reused
between scopes - conflict is resolved by preferring the innermost scope for a
given identifier. Lexical scopes are set in stone as the program is written.

JavaScript also has some support for dynamic scoping that is resolved during
program runtime, but let us put that aside for time being.

Introducing redundant lexical scopes with repeating identifiers is often done
for code obfuscation purposes, as it makes code hard to read and understand.
This motivates us to learn how to gain clarity when such scope obfuscation
technique is applied on client-side JavaScript code that we want to reverse 
engineer.

Since Babel parses the JS code into data model representing logical structure
of the code, it also has a capability to represent lexical scopes via `Scope`
object. Furthermore, Babel is able to handle scope bindings - relations between
identifiers and scopes. Through a scope binding we can find the usage of
variable name or some other identifier to track down where in the code that
identifier is being referenced. Thus we have all the tools to programmatically 
disambiguate between multiple identifiers across nested scopes and convert 
the code into a more readable form.

Let us use [ASTExplorer](https://astexplorer.net) with Chrome DevTools to
explore scopes and bindings. Put the following JS snippet in there:

```javascript
let x = 10;
let y = 20;

{
  let y = 30;
  console.log(x + y);
}

console.log(x + y);
```

[Screenshot 1](/2023-01-25_16.08.58.png)

We can see that there is no data about scopes and bindings in the final AST
that Babel parser outputs. There's a small trick to getting to that in 
ASTExplorer. First, we need to turn on the tranform sections and make a small
AST visitor function (within provided boilerplate) that prints scopes/bindings
for the AST nodes we are interested in. Let us see the `Scope` object for
the root AST node - `Program`:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "ast-transform", // not required
    visitor: {
      Program(path) {
        console.log(path.scope);
      }
    }
  };
}
```

To see what `console.log()` prints, we must switch on Chrome DevTools panel
and select Console tab. Some properties or interest are:

* `block` - AST node for code block (`BlockStatement`) or something else (e.g.
`Program`) that limits the scope.
* `bindings` - mapping of identifier names to `Binding` objects associated 
with the current scope.
* `globals` - list of AST nodes that are associated with the global scope;
current scope inherits them.
* `path` - a `NodePath` object that references back to the visited node and its
position within AST.

[Screenshot 2](/2023-01-25_16.18.57.png)

Some interesting properties of `Binding` object are:

* `identifier` - an `Identifier` node for the identifier in question (constant
name in this case)
* `path` - a `NodePath` object for AST node that introduces this identifier into
scope.
* `referenced` - flag to check if identifier has been referenced.
* `references` - number of references to identifier within the scope.
* `referencePaths` - an array of `NodePath` objects that are associated with the 
current identifier being referenced within the scope.

[Screenshot 3](/2023-01-25_16.18.57.png)

Note that for `x` we have 2 references and for `y` we have only one reference.
That should be expected, as in the inner lexical scope there is new declaration
of `y` that overrides the declaration of `y` in the outer scope.

These two constants that are both named `y` require further attention. Let us
take a deeper look into their scopes and bindings. Update the visitor function
in the bottom left corner to the following:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "ast-transform", // not required
    visitor: {
      VariableDeclarator(path) {
        if (path.node.id.name == "y") {
          console.log(path.scope);
          console.log("PARENT", path.scope.parent);
        }
      }
    }
  };
}
```

We are visiting `VariableDeclarator` nodes, but we are only interested in the
ones that declare `y`. For these, we log the current scope and parent scope.
In our example, parent scope is the scope for entire program and child scope
is within the curly braces.

[Screenshot 4](/2023-01-25_21.48.07.png)

To check for identifier name duplication, we can look into parent scope bindings
and see if there's a binding for another identitifier with the same name that
is being overridden. To prevent identifiers from being overriden we can rename
the new identifiers in child scopes. Let me show an example of Babel transform
that would do this:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "ast-transform", // not required
    visitor: {
      VariableDeclarator(path) {
        let idName = path.node.id.name;
        let parentScope = path.scope.parent;
        if (!parentScope) return;
        if (parentScope.getBinding(idName)) {
          let newName = path.scope.generateUidIdentifier(idName);
          path.scope.rename(idName, newName.name);
        }
      }
    }
  };
}
```

This transform modifies the snippet so that constant name duplication goes
away:

```javascript
let x = 10;
let y = 20;
{
  let _y = 30;
  console.log(x + _y);
}
console.log(x + y);
```

We used `Scope.rename()` method to rename the constant within the scope 
(covering both the declaration and statement that uses it) to a name that does
not duplicate with constant name in a parent scope. To save us from the hassle
of generating unique names, Babel provides us `Scope.generateUidIdentifier()`
method that we used to get a new `Identifier` node. Fixing name duplication 
turned out to be just a few lines of code.

Note that in some cases you may need to call `crawl()` on current or parent 
scope to make it update all the JS statements that reference the identifier
that has just been renamed.

Let us get more serious now by applying DefendJS scope obfuscation feature:

```
$ cp 1.js 6.js  
$ defendjs --input 6.js --features scope --output . 
```

The obfuscated version of the code is now like this:

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
        a[0] = 10;
        a[1] = 20;
        a[2] = 30;
        console.log(a[0] + a[2]);
        console.log(a[0] + a[1]);
    }
}())
```

Applying the current Babel transform does rename some variables in the junk
functions, but code stays mostly the same:

```javascript
(function () {
  {
    {
      function b(a, b) {
        return Array.prototype.slice.call(a).concat(Array.prototype.slice.call(b));
      }

      function c() {
        var _a = arguments[0],
            _c = Array.prototype.slice.call(arguments, 1);

        var _b = function () {
          return _a.apply(this, _c.concat(Array.prototype.slice.call(arguments)));
        };

        _b.prototype = _a.prototype;
        return _b;
      }

      function d(a, b) {
        return Array.prototype.slice.call(a, b);
      }

      function e(b) {
        var _c2 = {};

        for (var _a2 = 0; _a2 < b.length; _a2 += 2) {
          _c2[b[_a2]] = b[_a2 + 1];
        }

        return _c2;
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
    var _a3 = [];
    _a3[0] = 10;
    _a3[1] = 20;
    _a3[2] = 30;
    console.log(_a3[0] + _a3[2]);
    console.log(_a3[0] + _a3[1]);
  }
})();
```

Can we remove these junk functions that do not get called anywhere?
Let us try reworking the transform.

Remember that `Binding` object also keeps track of references to the
identifier in question? We can remove these functions based on them not being
referenced anywhere:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "ast-transform", // not required
    visitor: {
      FunctionDeclaration(path) {
        let fnName = path.node.id.name;
        let binding = path.scope.getBinding(fnName);
        if (!binding.referenced) path.remove();
      }
    }
  };
}

```

Now the code in the output is like this:

```javascript
(function () {
  {
    {
      function b(a, b) {
        return Array.prototype.slice.call(a).concat(Array.prototype.slice.call(b));
      }

      function c() {
        var a = arguments[0],
            c = Array.prototype.slice.call(arguments, 1);

        var b = function () {
          return a.apply(this, c.concat(Array.prototype.slice.call(arguments)));
        };

        b.prototype = a.prototype;
        return b;
      }
    }
    var a = [];
    a[0] = 10;
    a[1] = 20;
    a[2] = 30;
    console.log(a[0] + a[2]);
    console.log(a[0] + a[1]);
  }
})();
```

All but two junk functions got removed. A closer look into the remaining 
functions reveals that they are referencing themselves. Furthermore, we ran
into a weird feature of JavaScript: [`var` statements](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/var)
that are able to transcend the child scope and set the variable in a more global
scope. For example, the following code snippet from Mozilla developer portal 
counter-intuitively prints `2` twice:

```javascript
var x = 1;

if (x === 1) {
  var x = 2;

  console.log(x);
  // Expected output: 2
}

console.log(x);
// Expected output: 2

```

In the currently deobfuscated code `b()` references itself and `c()` references
`b()` (and also itself) through `var` statement. 

At the moment I can't think of a solution to resolve this kind of circular
references, but we already made some progress. We can see that both remaining
functions are not called anywhere and don't really do anything. Thus it is safe
to disregard them for time being.

Note however that Babel does not track scopes across files. It can only work 
with one file at a time. 
