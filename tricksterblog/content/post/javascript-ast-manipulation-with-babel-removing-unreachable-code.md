+++
author = "rl1987"
title = "JavaScript AST manipulation with Babel: removing unreachable code"
date = "2022-08-28"
tags = ["security", "reverse-engineering", "javascript"]
+++

Unreachable parts can be injected into JavaScript source as a form of obfuscation.
We will go through a couple of simple examples to show how the unreachable code paths
can be removed at Abstract Syntax Tree level for reverse engineering purposes.

For the first example, let us consider the following code:

```javascript
if (1 == 2) 
    console.log("1 == 2");

if (1 == 1) {
    console.log("1 == 1");
} else if (1 == 2) {
    console.log("1 == 2");
} else { 
    console.log("Unreachable as well");
}

1 == 1 ? console.log("yes") : console.log("no");

console.log("Hello");
```

Running it will produce three lines of output:

```
$ node dead_branches.js 
1 == 1
yes
Hello
```

We want to simplify it to the point of having only three `console.log()` calls in the
cleaned up version of the script.

Let us copy-paste this code into [AST Explorer](https://astexplorer.net/) to see what
it looks like when parsed into Babel AST data model. We notice that if statements
are parsed into `IfStatement` node and that line with question mark (conditional/ternary
operator) is parsed into `ConditionalExpression` node. Both of these nodes have `test`
property for representing condition itself, `consequent` property for part of the code
that would run if condition was true and `alternate` property for the code that would run
otherwise. The `alternate` property might be null if there was no `else` block in the if
statement or it might be pointing to another `IfStatement` node if we have multiple
conditions that the code tries to match against. Both branches of If statement or conditional
expression may point to `BlockStatement` node if there's a block of statements to be executed.

[Screenshot 1](/2022-08-27_21.14.44.png)

In our sample code `1 == 2` will always be false and `1 == 1` will always be true. To make
things easier for us, Babel provides a way to evaluate if stuff in `test` is "truthy".

All of this informs us on how to implement our cleanup code:

```javascript
const fs = require("fs");

const parser = require("@babel/parser");
const generate = require("@babel/generator").default;
const traverse = require("@babel/traverse").default;
const types = require("@babel/types");

let js = fs.readFileSync("dead_branches.js", "utf-8");

const ast = parser.parse(js);

traverse(ast, {
    "ConditionalExpression|IfStatement": function(path) {
        let isTruthy = path.get("test").evaluateTruthy();
        let node = path.node;

        if (isTruthy) {
            if (types.isBlockStatement(node.consequent)) {
                path.replaceWithMultiple(node.consequent.body);
            } else {
                path.replaceWith(node.consequent);
            }
        } else if (node.alternate != null) {
            if (types.isBlockStatement(node.alternate)) {
                path.replaceWithMultiple(node.alternate.body);
            } else {
                path.replaceWith(node.alternate);
            }
        } else {
            path.remove();
        }
    }
});

let clean = generate(ast).code;

fs.writeFileSync("no_dead_branches.js", clean);
```

We use `ConditionalExpression|IfStatement` string value as a key to match our visitor
function to both kinds of nodes we want to modify when traversing the AST. We use
`evaluateTruthy()` method to check if condition in `test` evaluates to Boolean true.
If it does, then we replace the If statement or conditional expression with the code
under the positive branch. This removes the If statement (or conditional expression)
and all the negative branches (if there are any). If it does not evaluate to Boolean
true value, we need to check if `alternate` points to `else` part - we modify the AST
to leave this part only. If `alternate` is null then we remove the entire shebang (this
applies to the very first If statement in the sample code). If there's block
statement on the relevant branch, we need to replace the parent node with all the nodes
in the `body` of that `BlockStatement` node.

Running this deobfuscation code produces the following cleaned-up JS code:

```javascript
console.log("1 == 1");
console.log("yes");
console.log("Hello");
```

Another example will be about unreachable functions that are never going to be executed.

Consider the following code:

```javascript
function dead1(a, b) {
    return a + b + 1;
}

function dead2() {
    console.log("!!");
}

function dead3() {
    dead1(1, 2);
    dead2();
}

console.log("Hello");
```

We want all three functions removed. In AST Explorer we can see that Babel parses
each function into `FunctionDeclaration` node.

 We will use Babel `getBinding()` method to check if they are being referenced 
anywhere (in a way that heeds lexical scopes). But here's a little problem: 
`dead1()` and `dead2()` are being called by `dead3()` so they do have references 
to them. Out of three functions, only `dead3()` is not being references by any other 
code. We are going to address this (perhaps in hacky manner) by doing more than one pass
of AST traversal.

[Screenshot 2](/2022-08-27_21.42.06.png)

The code that cleans up these dead functions is as follows:

```javascript
const fs = require("fs");

const parser = require("@babel/parser");
const generate = require("@babel/generator").default;
const traverse = require("@babel/traverse").default;
const types = require("@babel/types");

var js = fs.readFileSync("dead_functions.js", "utf-8");
var ast;

do {
    ast = parser.parse(js);
    var removed = 0;
    traverse(ast, {
        FunctionDeclaration: function(path) {
            if (!path.scope.getBinding(path.node.id.name).referenced) {
                path.remove();
                removed++;
            }
        }
    });
    js = generate(ast).code;
} while (removed > 0);

let clean = generate(ast).code;

fs.writeFileSync("no_dead_functions.js", clean);
```

After running this script, we have the following clean version of the code:

```javascript
console.log("Hello");
```

