+++
author = "rl1987"
title = "JavaScript AST manipulation with Babel: AST modification APIs"
date = "2023-01-31"
draft = true
tags = ["security", "reverse-engineering", "javascript"]
+++

In previous posts about using Babel for JavaScript deobfuscation, we have
used `NodePath.replaceWith()` method to replace one node with another and
`NodePath.remove()` to remove a single node. Since AST and it's elements are
mutable, we can also modify the AST without traversing it. But there is more
to learn about AST modification than what we have seen before. We will go 
through some more AST modification APIs that should prove to be useful
when developing JS deobfuscators, so that we could have them in our toolbox.

`NodePath.replaceWithMultiple()` replaces a single node with a list of nodes.

`NodePath.replaceWithSourceString()` is a convenience method that takes a source
string and parses it for you when replacing the node. However this is 
inefficient and not recommended. There are better ways to convert a source
string (or template) into AST subtree.

We can also insert a node before or after the current node. 
`NodePath.insertBefore()` and `NodePath.insertAfter()` methods can be used for
that.

Sometimes there are AST node property arrays that contain multiple child nodes.
You may want to to add a single new entry to beginning or end of that array.
`NodePath.unshiftContainer()` prepends a new node and `NodePath.pushContainer()`
appends it to the end of array. However it might be bit confusing on how to use
these methods. Consider the following snippet that we want to change:

```javascript
function say_abc() {
  console.log("a");
  console.log("b");
  console.log("c");
}

say_abc();
```

Let's suppose we want to add `debugger;` before and after the `console.log()`
calls in the function. When we parse this code into AST, we can see that we 
have a following subtree:

* `FunctionDeclaration`
 * `body`: `BlockStatement`
   * `body`: `[]` (`ExpressionStatement`s)

[Screenshot 1](/2023-01-29_19.14.55.png)

We want to modify the function body, so we will get a `NodePath` for the
`BlockStatement` at `body` property of `FunctionDeclaration`. The exact array
we want to modify is `body` of `BlockStatement`. Thus we call the above
methods on `BlockStatement` object with two arguments: 1) node property name
(`body`) and 2) the node object we want to insert. In AST Explorer we
develop the following transform:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "ast-transform", // not required
    visitor: {
      FunctionDeclaration(path) {
        let body = path.get('body');
        body.unshiftContainer('body', t.debuggerStatement());
        body.pushContainer('body', t.debuggerStatement());
      }
    }
  };
}
```

As intended, this modifies the toy code snippet into the following:

```javascript
function say_abc() {
  debugger;
  console.log("a");
  console.log("b");
  console.log("c");
  debugger;
}

say_abc();
```

[Screenshot 2](/2023-01-29_19.12.58.png)
[Screenshot 3](/2023-01-29_19.15.54.png)

If for some reason you want to skip traversal of children of current node
(e.g. to avoid infinite loop when nodes are being added) you can call
`NodePath.skip()`. To completely stop the AST traversal, you can call
`NodePath.stop()`.
