+++
author = "rl1987"
title = "JavaScript AST manipulation with Babel: reducing nestedness, unflattening the CFG"
date = "2023-02-18"
draft = true
tags = ["security", "reverse-engineering", "javascript"]
+++

In computer science, control flow graph is a graph that represents order of
code block execution and transitions between blocks. For the purposes of todays
topic, vertices in such graph are basic blocks of code that are to be executed
consequentially and have no branching logic. Each basic block has an entry point
and exit point. Edges in control graph represent transitions between basic 
blocks.

Control flow graph flattening is an obfuscation technique that introduces
large switch statements within while-loops with basic blocks at each switch
case. Switch condition contains some logic to choose a switch case on runtime
and each switch case does something at the end of basic block to switch to 
next one.

Consider the following sample code from [obfuscator.io](https://obfuscator.io)
documentation:

```javascript
(function(){
    function foo () {
        return function () {
            var sum = 1 + 2;
            console.log(1);
            console.log(2);
            console.log(3);
            console.log(4);
            console.log(5);
            console.log(6);
        }
    }
    
    foo()();
})();
```

When we run obfuscation with "Control Flow Flattening" checkbox being on, we get
the following obfuscated version of this code:

```javascript
(function () {
    var _0x5b0ba5 = {
        'HThGl': '2|4|1|3|5|6|0',
        'Ssbzl': function (_0x113c5a, _0x2b9ca8) {
            return _0x113c5a + _0x2b9ca8;
        },
        'pWydz': function (_0x237610) {
            return _0x237610();
        }
    };
    function _0x11c3ac() {
        var _0x134393 = {
            'HwgBi': _0x5b0ba5['HThGl'],
            'YnoJz': function (_0x5ad206, _0x2b2bb5) {
                return _0x5b0ba5['Ssbzl'](_0x5ad206, _0x2b2bb5);
            }
        };
        return function () {
            var _0x11ba88 = _0x134393['HwgBi']['split']('|');
            var _0x143f46 = 0x0;
            while (!![]) {
                switch (_0x11ba88[_0x143f46++]) {
                case '0':
                    console['log'](0x6);
                    continue;
                case '1':
                    console['log'](0x2);
                    continue;
                case '2':
                    var _0x3c58ad = _0x134393['YnoJz'](0x1, 0x2);
                    continue;
                case '3':
                    console['log'](0x3);
                    continue;
                case '4':
                    console['log'](0x1);
                    continue;
                case '5':
                    console['log'](0x4);
                    continue;
                case '6':
                    console['log'](0x5);
                    continue;
                }
                break;
            }
        };
    }
    _0x5b0ba5['pWydz'](_0x11c3ac)();
}());

```

We put this code into [ASTExplorer](https://astexplorer.net) where we will
be learning how to deobfuscate it.

We see that the innermost block of input code has been split into smaller
basic blocks and distributed across switch-cases in the obfuscated version.
Furthermore, obfuscator.io introduces some supporting obfuscations into the
code to make the primary obfuscation technique harder to reverse. Our strategy
here is to chip away these secondary techniques until we get to the point
of attacking the CFG flattening, then simplify the code to something close
to original form. 

Since we also want to make the code less nested for easier readability, let's
start by replacing the outermost IIFE with all the code inside it. This is
accomplished with the following transform:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "ast-transform", // not required
    visitor: {
      ExpressionStatement(path) {
        if (!t.isProgram(path.parent)) return;
        let node = path.node;
        let expr = node.expression;
        if (!t.isCallExpression(expr)) return;
        let callee = expr.callee;
        if (!t.isFunctionExpression(callee)) return;
        let innerStatements = callee.body.body;
        path.replaceWithMultiple(innerStatements);
      }
    }
  };
}
```

We target `ExpressionStatement` as that is the object type for IIFE. In the visitor
we also check for some other conditions to make sure we are visiting the 
exact part of the code we want to change: parent node has to be `Program` and 
there has to be a `CallExpression` node at `expression` field that points to
`FunctionExpression` node in it's `callee` field. If that is the case, we take
all the statement nodes from body of `callee` and replace our currently visited
node with them by calling `replaceWithMultiple` out the `NodePath` object. To
sum it up, we replace one node high up in the AST with multiple nodes from 
subtree below it. This refactors away the outermost IIFE.

[TODO: screenshot]

In the while we see that the condition for looping is quite confusing: `!![]`.
When we try it in the JS REPL, we get that this merely is another way for 
representing `true`:

```
$ node
Welcome to Node.js v19.0.1.
Type ".help" for more information.
> !![]
true
```

At AST level we have two nested `UnaryExpression` nodes with `ArrayExpression`
in the innermost level.

So if this stuff evaluates to a Boolean constant, perhaps Babel can compute 
it for us? Turns out it can with `NodePath.evaluate()` method that we use in 
our next transformation:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "ast-transform", // not required
    visitor: {
      UnaryExpression(path) {
        let result = path.evaluate();
        if (result.confident) {
          path.replaceWith(t.valueToNode(result.value));
        }
      }
    }
  };
}
```

We must take care to check `confident` flag to make sure Babel is confident of
the result. We replace the `UnaryExpression`s - both of them - with the 
resulting values. There is no need to worry about re-traversing the AST nodes
after tree modification, as Babel does that for us automatically.

So now we have `while(true)` in the code. Another thing we want to get rid is 
bracket notation, so that we have `console.log()` in the code, not
`console["log"]()`. This was covered earlier in the blog and can be done with 
the following AST transform:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "ast-transform", // not required
    visitor: {
      CallExpression(path) {
        let prop = path.node.callee.property;

        if (t.isStringLiteral(prop)) {
          path.node.callee.property = t.identifier(prop.value);
          path.node.callee.computed = false;
        }
      }
    }
  };
}
```

We did some easy ones and now the code looks as follows:

```javascript
var _0x5b0ba5 = {
  'HThGl': '2|4|1|3|5|6|0',
  'Ssbzl': function (_0x113c5a, _0x2b9ca8) {
    return _0x113c5a + _0x2b9ca8;
  },
  'pWydz': function (_0x237610) {
    return _0x237610();
  }
};

function _0x11c3ac() {
  var _0x134393 = {
    'HwgBi': _0x5b0ba5['HThGl'],
    'YnoJz': function (_0x5ad206, _0x2b2bb5) {
      return _0x5b0ba5.Ssbzl(_0x5ad206, _0x2b2bb5);
    }
  };
  return function () {
    var _0x11ba88 = _0x134393['HwgBi'].split('|');

    var _0x143f46 = 0x0;

    while (true) {
      switch (_0x11ba88[_0x143f46++]) {
        case '0':
          console.log(0x6);
          continue;

        case '1':
          console.log(0x2);
          continue;

        case '2':
          var _0x3c58ad = _0x134393.YnoJz(0x1, 0x2);

          continue;

        case '3':
          console.log(0x3);
          continue;

        case '4':
          console.log(0x1);
          continue;

        case '5':
          console.log(0x4);
          continue;

        case '6':
          console.log(0x5);
          continue;
      }

      break;
    }
  };
}

_0x5b0ba5.pWydz(_0x11c3ac)();

```

But the thing is, we still have these JS objects introducing indirection in the
code. In one case, a pipe-separated case order list is being referenced. In 
other cases, we have some auxillary functions being indirectly referenced.
To clean this up, we must further improve code from the previous post. In this
case, we need to do two things: 1) replace references to string literal with
actual value and 2) move out these nested functions out of the objects and
give them some names, so that they could be called directly without referencing
these objects. After that is done, we can remove the objects `_0x134393` and
`_0x5b0ba5` as they won't be needed anymore.

So the code to do this is as follows:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "ast-transform", // not required
    visitor: {
      VariableDeclarator(path) {
        let node = path.node;
        if (!node.init) return;
        if (!t.isObjectExpression(node.init)) return;
        let binding = path.scope.getBinding(node.id.name);
        if (!binding.constant) return;
        let properties = node.init.properties;
        if (!properties) return;
        
        let kv = new Object();
                
        for (let prop of properties) {
          if (!t.isStringLiteral(prop.key)) return;
          let key = prop.key.value;
          if (!t.isFunctionExpression(prop.value) && !t.isStringLiteral(prop.value)) return;
          let value = prop.value;
          kv[key] = value;
        }
                                
        for (let refPath of binding.referencePaths) {
          if (!refPath.parentPath) return;
          let parentNode = refPath.parentPath.node;
          let key = parentNode.property.name;
          if (!key) key = parentNode.property.value;
          let value = kv[key];
		          
          if (t.isStringLiteral(value)) {
            refPath.parentPath.replaceWith(value); 
          } else if (t.isFunctionExpression(value)) {
            let fnName = key;
            // https://babeljs.io/docs/en/babel-types#functiondeclaration
            let functionDecl = t.functionDeclaration(
              t.identifier(key),
              value.params,
              value.body,
              value.generator,
              value.async
            );
            
            let parentOfDecl = path.parentPath.parentPath;
            parentOfDecl.unshiftContainer("body", functionDecl);
            refPath.parentPath.replaceWith(t.identifier(fnName)); 
          }
        }
        
        path.remove();
      } 
    }
  };
}
```

As in previous post, we use scopes and bindings for replacing the references.
The new part is function creation and insertion into `body` of AST node two 
levels up from the `VariableDeclarator` that we are visiting. This target node
will be either `Program` or `FunctionExpression`, thus it is safe to assume
it will have a `body` property with array of AST nodes. We also make sure
that indirect function calls now are pointed to the new function that we 
reconstructed from the code nested in the object.

We are really getting ready to our final strike. The code now looks like this:

```javascript
function pWydz(_0x237610) {
  return _0x237610();
}

function Ssbzl(_0x113c5a, _0x2b9ca8) {
  return _0x113c5a + _0x2b9ca8;
}

function _0x11c3ac() {
  function YnoJz(_0x5ad206, _0x2b2bb5) {
    return Ssbzl(_0x5ad206, _0x2b2bb5);
  }

  return function () {
    var _0x11ba88 = '2|4|1|3|5|6|0'.split('|');

    var _0x143f46 = 0x0;

    while (true) {
      switch (_0x11ba88[_0x143f46++]) {
        case '0':
          console.log(0x6);
          continue;

        case '1':
          console.log(0x2);
          continue;

        case '2':
          var _0x3c58ad = YnoJz(0x1, 0x2);

          continue;

        case '3':
          console.log(0x3);
          continue;

        case '4':
          console.log(0x1);
          continue;

        case '5':
          console.log(0x4);
          continue;

        case '6':
          console.log(0x5);
          continue;
      }

      break;
    }
  };
}

pWydz(_0x11c3ac)();
```

We have `_0x143f46` variable starting at 0 and getting incremented by one per
each iteration of while loop. This counter is used to pick which switch case is
to be executed at each iteration. `_0x11ba88` is an array with case indices
as numeric strings. But we have one inconvenience here. This array is not 
being hardcoded directly (like `["2", "4", "1", "3", "5", "6", "0"]`), but
computed by splitting a pipe-separated string. Let us do one more AST transform
to convert this line into a form we need:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "ast-transform", // not required
    visitor: {
      VariableDeclarator(path) {
        let node = path.node;
        let init = node.init;
        if (!init || !t.isCallExpression(init)) return;
        let callee = init.callee;
        let obj = callee.object;
        if (!t.isStringLiteral(obj)) return;
        let prop = callee.property;
        if (!t.isIdentifier(prop)) return;
        if (prop.name != "split") return;
        let args = init.arguments;
        if (args.length != 1) return;
        if (!t.isStringLiteral(args[0])) return;

        let strToSplit = obj.value;
        let separator = args[0].value;
        
        let components = strToSplit.split(separator).map(t.valueToNode);
        
        node.init = t.arrayExpression(components);
      }
    }
  };
}
```

We do our work inside visitor in a similar way as before. We pick the right
AST node by unwrapping few levels below it and checking for conditions to make
sure we are at right point in the tree. Then we extract the string value, split
it and create an array with final values (represented by `StringLiteral` nodes)
that gets assigned to `init` property of relevant `VariableDeclarator` node.
Since AST requires node objects, not JS strings we convert values to nodes
with a little trick from functional programming - a 
[`map()` function](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/map).

As we wanted, the line that declares case order array now is like this:

```javascript
    var _0x11ba88 = ["2", "4", "1", "3", "5", "6", "0"];
```

We're ready to unflatten the CFG now. We got the directly hardcoded array of
case numbers in the order they will be executed and we got the switch statement
nested in a while loop that executes them until it runs out of cases in the
list. So we got to replace that while loop with all the little basic blocks
joined together in the order they would be executed at runtime. 

This is accomplished by the following transform:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "ast-transform", // not required
    visitor: {
      WhileStatement(path) {
        let whileStmt = path.node;
        let parentBody = path.parent.body;
        let bodyBlock = whileStmt.body;
        let bodyParts = bodyBlock.body;
        if (bodyParts.length == 0) return;
        if (!t.isSwitchStatement(bodyParts[0])) return;
        let switchStmt = bodyParts[0];
        let switchCases = switchStmt.cases;
        
        let basicBlocksByCase = {};
        
        for (let switchCase of switchCases) {
          let key = switchCase.test.value;
          basicBlocksByCase[key] = switchCase.consequent;
        }
        
        let arrayName = switchStmt.discriminant.object.name;
        let parentScope = path.parentPath.scope;
        let binding = parentScope.getBinding(arrayName);
        
        let arrayExpr = binding.path.node.init;
        let order = arrayExpr.elements.map((stringLiteral) => stringLiteral.value)
      
        let stuffInOrder = [];
        
        for (let caseNum of order) {
          let basicBlock = basicBlocksByCase[caseNum];
          stuffInOrder.push(...basicBlock); // https://stackoverflow.com/a/1374131/1044147
        }
        
        path.replaceWithMultiple(stuffInOrder);
        binding.path.remove();
      },
      ContinueStatement(path) {
        path.remove();
      }
    }
  };
}
```

Note how we get the array name from `discriminant.object` of the 
`WhileStatement` to get the `ArrayExpression` node from further up in the code
by accessing parent node scope and it's binding. 

There are two stages of code reconstruction: 1) we gather all the basic blocks
into object, keyed by their case numbers and 2) we unite them into list of nodes
in the order of cases that we extracted from `ArrayExpression` object.
`WhileStatement` is replaced with this array of nodes, resulting in the 
original order of statements. Array that lists case numbers is removed 
afterwards as it's no longer needed. We also remove `ContinueStatement` nodes
as they were only needed in the while-switch structure that we had in obfuscated
code.

The deobfuscated code is now as follows:

```javascript
function pWydz(_0x237610) {
  return _0x237610();
}

function Ssbzl(_0x113c5a, _0x2b9ca8) {
  return _0x113c5a + _0x2b9ca8;
}

function _0x11c3ac() {
  function YnoJz(_0x5ad206, _0x2b2bb5) {
    return Ssbzl(_0x5ad206, _0x2b2bb5);
  }

  return function () {
    var _0x143f46 = 0x0;

    var _0x3c58ad = YnoJz(0x1, 0x2);

    console.log(0x1);
    console.log(0x2);
    console.log(0x3);
    console.log(0x4);
    console.log(0x5);
    console.log(0x6);
  };
}

pWydz(_0x11c3ac)();
```

We still have a bit of nestedness and indirection, but this code does print
numbers 1 to 6 in the same way that original code did and is quite readable.

