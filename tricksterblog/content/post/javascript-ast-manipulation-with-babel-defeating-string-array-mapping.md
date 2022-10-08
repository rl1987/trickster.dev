+++
author = "rl1987"
title = "JavaScript AST manipulation with Babel: defeating string array mapping"
date = "2022-10-08"
draft = true
tags = ["javascript", "scraping"]
+++

One Javascript obfuscation technique that can be found in the wild is string array mapping.
It entails gathering all the string constants from the code into an array and modifying the
code so that string literals are accesssed by referencing the array at various indices instead
of having string literals being used directly. Like with previously discussed obfuscation techniques
we will be exploring it in isolation, but in real automation-hostile sites it will most likely be
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

