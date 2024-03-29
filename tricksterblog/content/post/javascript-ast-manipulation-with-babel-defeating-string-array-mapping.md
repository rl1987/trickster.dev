+++
author = "rl1987"
title = "JavaScript AST manipulation with Babel: defeating string array mapping"
date = "2022-10-08"
tags = ["ast", "javascript", "scraping"]
+++

One Javascript obfuscation technique that can be found in the wild is string array mapping.
It entails gathering all the string constants from the code into an array and modifying the
code so that string literals are accesssed by referencing the array at various indices instead
of having string literals being used directly. Like with previously discussed obfuscation techniques
we will be exploring it in isolation, but in real websites it will most likely be
used in combination with another techniques.

Let us consider the following code:

```javascript
console.log("Hello Venus");
console.log("Hello Earth");
console.log("Hello Mars");
```

Obfuscating this with [Javascript Obfuscator](https://javascriptobfuscator.com/Javascript-Obfuscator.aspx)
"Move Strings" option turns it into the following obfuscated version:

```javascript
var _0x3baf=["Hello Venus","log","Hello Earth","Hello Mars"];console[_0x3baf[1]](_0x3baf[0]);console[_0x3baf[1]](_0x3baf[2]);console[_0x3baf[1]](_0x3baf[3])
```

[Screenshot 1](/2022-10-07_14.11.47.png)

We have a single line consisting of multiple JS statements. Let us break this down for easier readability:

```javascript
var _0x3baf=["Hello Venus","log","Hello Earth","Hello Mars"];
console[_0x3baf[1]](_0x3baf[0]);
console[_0x3baf[1]](_0x3baf[2]);
console[_0x3baf[1]](_0x3baf[3])
```

We can see that `_0x3baf` is an array of strings with all the string literals that were used in the
code (including `log` as `console.log` is equivalent to `console["log"]`) and that is being referenced
in further statements. Let us analyse this code in ASTExplorer.

[Screenshot 2](/2022-10-08_10.10.10.png)

Whenever the aforementioned string array is being used to get a string constant, we have a `MemberExpression`
node in the tree with `object` instance variable being `Identifier` for the array name and `property` being
`NumericLiteral` with index value. Of course, not every reference to an array will be related to string
obfuscation, so we will have to check in our deobfuscation script if the array element at given index is indeed
a string literal.

Like in previous posts, our code will have three parts:

1. Reading the JS code and parsing it into Babel AST data model.
2. Traversing the AST and modifying it using a visitor function.
3. Regenerating the code from AST.

In step 2 we will be using `getBinding()` method to get a binding of an array name. This will let us dig up
an `ArrayExpression` node that has all the array elements so that we can perform an AST node substitution.

The code to deobfuscate this simple case of string array mapping is as follows:

```javascript
const fs = require("fs");

const parser = require("@babel/parser");
const generate = require("@babel/generator").default;
const traverse = require("@babel/traverse").default;
const types = require("@babel/types");

let code = fs.readFileSync("obfuscated.js", "utf-8");

const ast = parser.parse(code);

traverse(ast, {
    MemberExpression: function(path) {
        if (!path.node.property) return;
        if (!types.isNumericLiteral(path.node.property)) return;

        let idx = path.node.property.value;

        let binding = path.scope.getBinding(path.node.object.name);
        if (!binding) return;
        
        if (types.isVariableDeclarator(binding.path.node)) {
            let array = binding.path.node.init;
            if (idx >= array.length) return;

            let member = array.elements[idx];

            if (types.isStringLiteral(member)) {
                path.replaceWith(member);
            }
        }
    }
});

fs.writeFileSync("clean.js", generate(ast).code);

```

We tie our visitor function to `MemberExpression` node type as that corresponds to parts of AST
we want to modify. We make sure that `property` is indeed a numeric literal and take an array
index from there. Next, we get the binding based on array name. On success, binding will point
to a relevant `VariableDeclarator` node (through `path` and `node`) that points to the
`ArrayExpression` node through `init` property. We have a reference to an array and we also
have an index. We get the the array member. If it is indeed a string literal we perform the node
substitution.

The deobfuscated code is as follows:

```javascript
var _0x3baf = ["Hello Venus", "log", "Hello Earth", "Hello Mars"];
console["log"]("Hello Venus");
console["log"]("Hello Earth");
console["log"]("Hello Mars");
```

By working with Abstract Syntax Tree we were able to treat the code as data structure that
can be manipulated to simplify it for undoing the obfuscation.
