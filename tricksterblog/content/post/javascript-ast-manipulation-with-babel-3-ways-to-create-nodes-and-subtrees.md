+++
author = "rl1987"
title = "JavaScript AST manipulation with Babel: 3 ways to create nodes and subtrees"
date = "2023-01-31"
draft = true
tags = ["security", "reverse-engineering", "javascript"]
+++

When doing Javascript deobfuscation work at AST level one will need to create
new parts of AST for replacing the existing parts of AST being processed. We
will go through 3 ways of doing that. 

For the sake of an example, let us try to build and AST for the following
JS snippet:

```javascript
debugger;
console.log("!")
debugger;
```

Babel parses this into two `DebuggerStatement` nodes and and one 
`ExpressionStatement` node. 

[TODO: screenshot]

We don't need to worry about `File` and `Program` and should only focus on
the program body that contains the following child nodes:

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

Just instantiate the node objects
---------------------------------

WRITEME

Use Babel template
------------------

WRITEME

Parse the source code
---------------------

WRITEME

