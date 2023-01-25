+++
author = "rl1987"
title = "JavaScript AST manipulation with Babel: untangling scope confusion"
date = "2023-01-31"
draft = true
tags = ["security", "reverse-engineering", "javascript"]
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

[TODO: screenshot]

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

[TODO: screenshot]

Some interesting properties of `Binding` object are:

* `identifier` - an `Identifier` node for the identifier in question (constant
name in this case)
* `path` - a `NodePath` object for AST node that introduces this identifier into
scope.
* `referenced` - flag to check if identifier has been referenced.
* `references` - number of references to identifier within the scope.
* `referencePaths` - an array of `NodePath` objects that are associated with the 
current identifier being referenced within the scope.

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

WRITEME: real-worldish example on ASTExplorer

Note however that Babel does not track scopes across files. It can only work 
with one file at a time.
