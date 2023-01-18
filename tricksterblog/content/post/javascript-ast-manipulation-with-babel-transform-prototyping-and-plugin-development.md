+++
author = "rl1987"
title = "JavaScript AST manipulation with Babel: transform prototyping and plugin development"
date = "2023-01-18"
tags = ["security", "reverse-engineering", "javascript"]
+++

In previous posts we have went through several JavaScript obfuscation techniques
and how they could be reversed by applying Abstract Syntax Tree transformations.
AST manipulation is a powerful skill that is of particular importance in
certain kinds of grayhat programming projects. Earlier, we have focused on how
exactly AST could be changed to undo specific kinds of obfuscations. This time,
however, we will take a bit broader look into Babel to see how it facilitates
development of AST manipulation code that goes beyond a single AST 
transformation.

In [one of the posts](/post/javascript-ast-manipulation-with-babel-the-first-steps)
we have shown some trivial examples of AST manipulation:
* Undoing hexadecimal string encoding
* Converting bracket notation to dot notation
* Removing excessive semi-colons from the code

First, let me show a way to prototype AST transforms in 
[ASTExplorer](https://astexplorer.net). Let us put the following code in there:

```javascript
console["log"]("\x41\x42\x43"); // ABC
;;;;;console.log("123");;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
```

Make sure that JavaScript is chosen in the language drop-down menu and 
`@babel/parser` is selected in the parser drop-down. Press the "Transform"
switch and choose `babelv7`. Now we have two new UI sections here. 

[Screenshot 1](/2023-01-17_19.56.13.png)

On the bottom left, there's a transform code editing section. By default
ASTExplorer gives you the following example code that reverses the order
or characters in identifier names:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "ast-transform", // not required
    visitor: {
      Identifier(path) {
        path.node.name = path.node.name.split("").reverse().join("");
      }
    }
  };
}

```

On the bottom right section we have the JS code that is the result of this
transformation.

The current transform by itself is quite useless, but we can change it to our
needs. Note that there is no boilerplate code for reading the JS source code
and writing it back into files. Just the AST transform that is the core
of what we are doing here.

Let us change the visitor function to undo hexadecimal string encoding:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "ast-transform", // not required
    visitor: {
      StringLiteral: function (path) {
        path.node.extra.raw = '"' + path.node.extra.rawValue + '"';
      }
    }
  };
}

```

We can see that `console["log"]("\x41\x42\x43");` from the input indeed became
`console["log"]("ABC");` in the output.

[Screenshot 2](/2023-01-17_20.20.35.png)

Since other two changes we want to make work on different node classes, we
can extend the top `visitor` object to include them as well:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "ast-transform", // not required
    visitor: {
      StringLiteral: function (path) {
        path.node.extra.raw = '"' + path.node.extra.rawValue + '"';
      },
      CallExpression: function (path) {
        let prop = path.node.callee.property;

        if (t.isStringLiteral(prop)) {
          path.node.callee.property = t.Identifier(prop.value);
          path.node.callee.computed = false;
        }
      },
      EmptyStatement: function (path) {
        path.remove();
      }
    }
  };
}

```

This cleaned up the code into the following form:

```javascript
console.log("ABC"); // ABC

console.log("123");
```

[Screenshot 3](/2023-01-17_20.24.51.png)

That's nice, but our transform code is not particularly clean, as we are
performing three different kinds of changes in one go. It does not matter much
for simple example like this, but real-world deobfuscators will involve far
more complexity and should be written with one of the best programming practices
in mind: keeping stuff separate without letting it became a single intractable
mess of spaghetti code. Thus we want a better structure in our code.

Babel is developed with plugin architecture in mind. Babel plugin is pluggable
piece of code that does a single change to the AST being processed. In our
example, there would be one plugin for undoing the hexadecimal string encoding,
another for converting bracket notation to do notation and third one for 
removing `EmptyStatement` nodes. There's also a concept of preset - a 
collection of plugins that make up some greater workflow, such as converting
the code between JavaScript dialects or undoing the entire set of obfuscation
techniques that antibot vendor is applying.

Let us save the input code from AST Explorer into input.js and write a single
deobfuscator that benefits from Babel plugin architecture to a greater degree.

Consider the following code:

```javascript
const fs = require("fs");
const path = require("path");

const babel = require("@babel/core");
const t = require("@babel/types");

const result = babel.transformFileSync(path.join(__dirname, 'input.js') , {
    plugins: [{
        name: "undo_hexadecimal_strings",
        visitor: {
            StringLiteral: function (path) {
                path.node.extra.raw = '"' + path.node.extra.rawValue + '"';
            }
        }
    }, {
        name: "bracket_to_dot",
        visitor: {
            CallExpression: function (path) {
                let prop = path.node.callee.property;

                if (t.isStringLiteral(prop)) {
                    path.node.callee.property = t.Identifier(prop.value);
                    path.node.callee.computed = false;
                }
            }
        }
    }, {
        name: "rm_needless_semicolons",
        visitor: {
            EmptyStatement: function (path) {
                path.remove();
            }
        }
    }]
});

console.log(result.code);

fs.writeFileSync(path.join(__dirname, 'output.js'), result.code, 'utf-8');

```

In our previous code in the previous posts, we had parsing, AST traversal, 
code generation as separate steps, which is good for understanding what's going 
on in the code, but introduces a bit of repetitive boilerplate. Now we are using
`transformFileSync()` function that does all three steps for us. It takes 
a file path to input JS file and a list of plugins. Each plugin is a
named AST manipulation step that entails one or more visitor functions that are
associated with certain types of AST nodes. 

Asynchronous equivalent to this function would be `transformFile()`. There's
also `transform()`, `transformSync()` and `transformAsync()` that take JS code 
a string without reading it from the file. 

Plugin code can be quite long and complex, which makes us want to keep it in
one or more separate files. Babel allows that as well. Let us move the plugin
code out of the main script by creating new files for each plugin.

First plugin file (plugin\_unhex.js) would be as follows:

```javascript
const babel = require("@babel/core");
const t = require("@babel/types");

module.exports = function (babel) {
    return {
        name: "undo_hexadecimal_strings",
        visitor: {
            StringLiteral: function (path) {
                path.node.extra.raw = '"' + path.node.extra.rawValue + '"';
            }
        }
    }
};

```

Next file, plugin\_unbracket.js would be like this:

```javascript
const babel = require("@babel/core");
const t = require("@babel/types");

module.exports = function (babel) {
    return {
        name: "bracket_to_dot",
        visitor: {
            CallExpression: function (path) {
                let prop = path.node.callee.property;

                if (t.isStringLiteral(prop)) {
                    path.node.callee.property = t.Identifier(prop.value);
                    path.node.callee.computed = false;
                }
            }
        }
    }
};

```

The third and last plugin file would contain the following code:

```javascript
const babel = require("@babel/core");
const t = require("@babel/types");

module.exports = function (babel) {
    return {
        name: "rm_needless_semicolons",
        visitor: {
            EmptyStatement: function (path) {
                path.remove();
            }
        }
    }
};

```

By moving all three plugins to their own files, we can simplify the main script
to this:

```javascript
const fs = require("fs");
const path = require("path");

const babel = require("@babel/core");
const t = require("@babel/types");

const result = babel.transformFileSync(path.join(__dirname, 'input.js') , {
    plugins: [
        path.join(__dirname, 'plugin_unhex.js'),
        path.join(__dirname, 'plugin_unbracket.js'),
        path.join(__dirname, 'plugin_rm_empty.js')
    ]
});

console.log(result.code);

fs.writeFileSync(path.join(__dirname, 'output.js'), result.code, 'utf-8');

```

Now that is far cleaner and less nested than it was before.

Before we're finished here, you may want to know one neat trick in ASTExplorer.
When you call `console.log()` on a Babel object such as node, path, scope and
open Chrome DevTools you can inspect various properties to debug your 
transformations.

[Screenshot 4](/2023-01-17_22.07.48.png)

To learn more about Babel plugin development, see:

* [Babel plugin handbook](https://github.com/jamiebuilds/babel-handbook/blob/master/translations/en/plugin-handbook.md)
* [`@babel/core` documentation](https://babeljs.io/docs/en/babel-core)

