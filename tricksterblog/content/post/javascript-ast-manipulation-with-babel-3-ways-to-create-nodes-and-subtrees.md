+++
author = "rl1987"
title = "JavaScript AST manipulation with Babel: 3 ways to create nodes and subtrees"
date = "2023-01-23"
tags = ["security", "reverse-engineering", "javascript"]
+++

When doing Javascript deobfuscation work at AST level one will need to create
new parts of AST for replacing the existing parts of AST being processed. We
will go through 3 ways of doing that. 

For the sake of an example, let us try to build an AST for the following
JS snippet:

```javascript
debugger;
console.log("!")
debugger;
```

Babel parses this into two `DebuggerStatement` nodes and and one 
`ExpressionStatement` node. 

[Screenshot](/2023-01-23_14.41.51.png)

We don't need to worry about `File` and `Program` objects and should only focus
on the program body that contains the following child nodes:

1. `DebuggerStatement`
2. `ExpressionStatement`
      * `expression`: `CallExpression`
        * `callee`: `MemberExpression`
          * `object`: `Identifier`
            * `name`: `"console"`
          * `computed`: `false`
          * `property`: `Identifier`
            * `name`: `"log"`
      * `arguments`: `[]`
        1. `StringLiteral`
           * `extra`:
             * `rawValue`: `"!"`
           * `value`: `"!"`
3. `DebuggerStatement`

Once we build these three statements, we can replace some part of AST with
them. That will be shown as well.

Instantiate node objects, arrange them into tree
------------------------------------------------

In software development there is often a tradeoff to be made between simplicity
of the code and it's flexibility. We will start with the least simple, but most
flexible approach - explicitly instantiating AST node objects and arranging
them in a way that recreates the AST subtree above. 

We need to refer to spec for Babel AST objects and their properties in Babel 
codebase file [packages/babel-parser/ast/spec.md](https://github.com/babel/babel/blob/main/packages/babel-parser/ast/spec.md).
Furthermore, we need to check node creation APIs in 
[`@babel/types` documentation](https://babeljs.io/docs/en/babel-types).

By using the information in these two documents, we can write the following
code:

```javascript
const parser = require("@babel/parser");
const generate = require("@babel/generator").default;
const t = require("@babel/types");

const debugStmt1 = t.debuggerStatement();

const consoleId = t.identifier("console");
const logId = t.identifier("log");
const stringLiteral = t.stringLiteral("!");
const callee = t.memberExpression(consoleId, logId);
const callExpr = t.callExpression(callee, [ stringLiteral ]);
const exprStmt = t.expressionStatement(callExpr);

const debugStmt2 = { type: 'DebuggerStatement' };

const body = [ debugStmt1, exprStmt, debugStmt2 ];

const ast = parser.parse(""); // Parsing empty string creates AST with File and Program nodes.

ast.program.body = body;

console.log(ast);
console.log("==================");
console.log(generate(ast).code);

```

Note that we can build AST node objects either by using factory functions from
`@babel/types` or by defining them as JS objects directly. Compare how
`debugStmt1` and `debugStmt2` were created.

Running this Node.JS script prints the modified AST and the generated code:

```
$ node instantiate.js
Node {
  type: 'File',
  start: 0,
  end: 0,
  loc: SourceLocation {
    start: Position { line: 1, column: 0, index: 0 },
    end: Position { line: 1, column: 0, index: 0 },
    filename: undefined,
    identifierName: undefined
  },
  errors: [],
  program: Node {
    type: 'Program',
    start: 0,
    end: 0,
    loc: SourceLocation {
      start: [Position],
      end: [Position],
      filename: undefined,
      identifierName: undefined
    },
    sourceType: 'script',
    interpreter: null,
    body: [ [Object], [Object], [Object] ],
    directives: []
  },
  comments: []
}
==================
debugger;
console.log("!");
debugger;
```

Thus we have demonstrated a very basic example of JS code generation with Babel.

Use Babel template
------------------

[`@babel/template`](https://babeljs.io/docs/en/babel-template) module lets us
define a code template, parametrise it with AST nodes and create a subtree
from that. 

Let us generate the JS snippet using this approach:

```javascript
const parser = require("@babel/parser");
const generate = require("@babel/generator").default;
const t = require("@babel/types");
const template = require("@babel/template").default;

const exampleTempl = template(`
debugger;
console.log(%%msg%%);
debugger;
`);

const body = exampleTempl({
    msg: t.stringLiteral("!")
});

const ast = parser.parse("");

ast.program.body = body;

console.log(ast);
console.log("==================");
console.log(generate(ast).code);

```

We're getting the same output as from the previous script.

Parse the source code
---------------------

Sometimes you may want to add some code that does not depend on any context
is is fairly simple. Due to recursive structure of AST we can create a small
AST by parsing a JS snippet and plug it into where we want it to be in the 
bigger tree.  This is as simple and basic as can get and I don't think 
it warrants any sample code. However we must not forget that in some cases 
easy and simple way is the right way. 

