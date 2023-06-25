+++
author = "rl1987"
title = "Don't JSFuck with me: Part 3"
draft = true
date = "2023-06-25"
tags = ["security", "reverse-engineering", "ast", "javascript"]
+++

Previously on Trickster Dev:
 * [Part 1](/post/dont-jsfuck-with-me-part-1/)
 * [Part 2](/post/dont-jsfuck-with-me-part-2/)

By using AST transforms developed so far, JSFuck output for character `@` can 
be simplified to:

```javascript
[]["flat"]["constructor"]("return\"" + ([]["flat"]["constructor"]("return/false/")()["constructor"]("/") + [])[1] + [1] + [0] + [0] + "\"")();
```

What about other characters that have `null` value in the `MAPPING` object in
jsfuck.js? 

For `H` we have:

```javascript
[]["flat"]["constructor"]("return\"" + ([]["flat"]["constructor"]("return/false/")()["constructor"]("/") + [])[1] + [1] + [1] + [0] + "\"")();
```

For `J` we have:

```javascript
[]["flat"]["constructor"]("return\"" + ([]["flat"]["constructor"]("return/false/")()["constructor"]("/") + [])[1] + [1] + [1] + [2] + "\"")();
```

For `K` we have:

```javascript
[]["flat"]["constructor"]("return\"" + ([]["flat"]["constructor"]("return/false/")()["constructor"]("/") + [])[1] + [1] + [1] + [3] + "\"")();
```

For `~` we have:

```javascript
[]["flat"]["constructor"]("return\"" + ([]["flat"]["constructor"]("return/false/")()["constructor"]("/") + [])[1] + [1] + [7] + [6] + "\"")();
```

The code we end up is very similar and follows a clear pattern.

Again, we can use NodeJS REPL to verify that this crazy shebang evaluates back
to the original character:

```
> []["flat"]["constructor"]("return\"" + ([]["flat"]["constructor"]("return/false/")()["constructor"]("/") + [])[1] + [1] + [7] + [6] + "\"")();
'~'
```

Let us try to pick this stuff apart.

Due to type coercion, `[1] + [7] + [6]` part can be simplified to a single 
numeric string:

```
> [1] + [7] + [6]
'176'
```

Now what can we learn about code deeper in the statement?

```
> []["flat"]["constructor"]("return/false/")()
/false/
> []["flat"]["constructor"]("return/false/")()["constructor"]
[Function: RegExp]
> []["flat"]["constructor"]("return/false/")()["constructor"]("/")
/\//
> []["flat"]["constructor"]("return/false/")()["constructor"]("/") + []
'/\\//'
> ([]["flat"]["constructor"]("return/false/")()["constructor"]("/") + [])[1]
'\\'
```

This statement creates a regular expression object (`/false/`), accesses 
it's `contructor` property to get a corresponding constructor function object 
(`RegExp()`), calls it with parameter `/` (this results in new regular expression 
object), then add an empty array to a result to stringify it through type 
coercion. Resulting string is indexed to to extract a single backslash character.

Based on this, we can perform some manual simplifications to this code:

```
> []["flat"]["constructor"]("return\"" + ([]["flat"]["constructor"]("return/false/")()["constructor"]("/") + [])[1] + '176' + "\"")();
'~'
> []["flat"]["constructor"]("return\"" + (RegExp("/") + [])[1] + '176' + "\"")();
'~'
> []["flat"]["constructor"]("return\"" + '\\' + '176' + "\"")();
'~'
> []["flat"]["constructor"]("return\"\\176\"")();
'~'
```

What is the number 176 doing here? In the ASCII standard, octal 176 corresponds 
to character `~` (see ascii(7) manpage). After undoing this octal-encoding, code
gets even simpler:

```
> []["flat"]["constructor"]("return\"~\"")();
'~'
```

But what about this `[]["flat"]["constructor"]` part we have here? JSFuck web app
front page notes it is equivalent to calling `eval()`. Let us verify that for 
ourselves.

```
> []["flat"]
[Function: flat]
> typeof []["flat"]
'function'
> []["flat"]["constructor"]
[Function: Function]
> typeof []["flat"]["constructor"]
'function'
> []["flat"]["constructor"]("console.log(1)")
[Function: anonymous]
> []["flat"]["constructor"]("console.log(1)")()
1
undefined
> []["flat"]["constructor"] == Function
true
> Function("console.log(1)")()
1
undefined
```

So let us try to refactor this code bit by bit using Babel AST transformations.

First transformation is for converting `[]["flat"]["constructor"]("return/false/")()`
into `/false/`:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "simplify-false-regex", // not required
    visitor: {
      CallExpression(path) {
		const callExpr = path.node;
        if (callExpr.arguments.length != 0) return;
        if (!t.isCallExpression(callExpr.callee)) return;
        const calleeMemberExpr = callExpr.callee.callee;
        if (!t.isMemberExpression(calleeMemberExpr)) return;
        const memberExpr2 = calleeMemberExpr.object;
        if (!t.isMemberExpression(memberExpr2)) return;
        const arrayObj = memberExpr2.object;
        if (!t.isArrayExpression(arrayObj)) return;
        if (arrayObj.elements.length != 0) return;
        const property1 = memberExpr2.property;
        if (!t.isStringLiteral(property1)) return;
        if (property1.value != "flat") return;
        const property2 = calleeMemberExpr.property;
        if (!t.isStringLiteral(property2)) return;
        if (property2.value != "constructor") return;
        if (callExpr.callee.arguments.length != 1) return;
        const argStrLiteral = callExpr.callee.arguments[0];
        if (!t.isStringLiteral(argStrLiteral)) return;
        if (argStrLiteral.value != "return/false/") return;      
        path.replaceWith(t.regExpLiteral('false', ''));
      }
    }
  };
}
```

Now we need to deal with regexp constructor thing that accepts a string argument.
There's another transform for that:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "refactor-regex-constr", // not required
    visitor: {
      CallExpression(path) {
        const callExpr = path.node;
        if (callExpr.arguments.length != 1) return;
        const argument = callExpr.arguments[0];
        if (!t.isStringLiteral(argument)) return;
        const calleeMemberExpr = callExpr.callee;
        if (!t.isMemberExpression(calleeMemberExpr)) return;
        if (!t.isRegExpLiteral(calleeMemberExpr.object)) return;
        let property = calleeMemberExpr.property;
        if (!t.isStringLiteral(property)) return;
        if (property.value != "constructor") return;
        
        path.replaceWith(
          t.regExpLiteral(argument.value.replace('/', '\\/'), '')
        );
      }
    }
  };
}
```

Now we deal with addition of regular expression with empty array to stringify
the regular expression object. Current code from part 1 deals with similar
stuff, but is unable to cover what we have now. Thus we write one more
small transformation to only cover this case:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "regex-str", // not required
    visitor: {
      BinaryExpression(path) {
        const binExpr = path.node;
        const left = binExpr.left;
        if (!t.isRegExpLiteral(left)) return;
        const right = binExpr.right;
        if (!t.isArrayExpression(right)) return;
        if (right.elements.length != 0) return;
        
        const regexStr = String(RegExp(left.pattern));
        
        path.replaceWith(t.stringLiteral(regexStr));
      }
    }
  };
}
```

To convert `[]["flat"]["constructor"]()` into `eval()` calls we develop the
following transform:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "fix-eval", // not required
    visitor: {
      CallExpression(path) {
        let node = path.node;
        if (node.arguments.length != 1) return;
        if (!t.isStringLiteral(node.arguments[0])) return;
        let parent = path.parent;
        if (!t.isCallExpression(parent)) return;
        let callee = node.callee;
        if (!t.isMemberExpression(callee)) return;
        if (!t.isStringLiteral(callee.property)) return;
        let key1 = callee.property.value;
        if (!t.isMemberExpression(callee.object)) return;
        if (!t.isStringLiteral(callee.object.property)) return;
        let key2 = callee.object.property.value;
        if (key1 === "constructor" && (key2 === "filter" || key2 === "flat")) {
          let evalCallExpr = t.callExpression(t.identifier('eval'), node.arguments);
          path.parentPath.replaceWith(evalCallExpr);
        }
      }
    }
  };
}
```

To convert string-returning `eval()` calls into string literals we do one more
transformation:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "eval-return-str", // not required
    visitor: {
      CallExpression(path) {
        let node = path.node;
        if (!t.isIdentifier(node.callee)) return;
        if (node.callee.name != "eval") return;
        if (node.arguments.length != 1) return;
        if (!t.isStringLiteral(node.arguments[0])) return;
        
        let argStr = node.arguments[0].value;
        
        if (argStr.startsWith("return\"") && argStr.endsWith("\"")) {
          argStr = argStr.substr("return\"".length);
          argStr = argStr.substr(0, argStr.length-1);
          path.replaceWith(t.stringLiteral(argStr));
        }
      }
    }
  };
}
```

During this deobfuscation exercise, some more AST transforms were developed to
cover new edge cases as they emerge. It would be excessive to cover them all
in this post, as they all follow the pattern of matching the subtree for code
we want to change and modifying to simplify it.

At this point, we can talk about unifying all the code we have into deobfuscator
program that can be launched from a command line. Each AST transform we 
prototyped in AST Explorer can be trivially converted into Babel plugin by
changing couple lines in the code. For example, the `undo-string-trick`
transform becomes the following Babel plugin in file plugin\_undo\_string\_trick.js:

```javascript
const babel = require("@babel/core");
const t = require("@babel/types");

const logASTChange = require("./debug.js").logASTChange;

module.exports = function (babel) {
  return {
    name: "undo-string-trick", // not required
    visitor: {
      Identifier(path) {
        let node = path.node;
       	if (!t.isBinaryExpression(path.parent)) return;
        if (path.parent.operator != "+") return;
        if (node.name === "String") {
          let newNode = t.valueToNode(String(String));
          logASTChange("undo-string-trick", node, newNode);
          path.replaceWith(newNode);
        }
      }
    }
  };
}
```

You may notice that `logASTChange()` function is being imported from debug.js
file. This function is meant to show us how the code is being changed as the
transform is applied, so that we could see a step-by-step progress in the
standard output. The code in debug.js file is as follows:

```javascript
const generate = require("@babel/generator").default;

function logASTChange(pluginName, ast1, ast2) {
  const js1 = generate(ast1).code;
  const js2 = generate(ast2).code;

  console.log("PLUGIN NAME:", pluginName);
  console.log("FROM CODE:", js1);
  console.log("TO CODE:", js2);
}

module.exports = { logASTChange };
```

Code before and after the modification is being regenerated from AST form and
printed into standard output with the Babel plugin name.

In app.js file we have code that unites all the plugins into single program
with basic CLI:

```javascript
const fs = require("fs");
const path = require("path");
const process = require("process");

const babel = require("@babel/core");
const t = require("@babel/types");

if (process.argv.length != 4) {
  console.log("Usage:");
  console.log("node app.js <input_js> <output_js>");
  process.exit(0);
}

const input_js = process.argv[2];
const output_js = process.argv[3];

let js = fs.readFileSync(input_js, "utf-8");
console.log(js);
console.log("-----------------------------------------------------------------");

while (true) {
  const result = babel.transformSync(js, {
      plugins: [
        path.join(__dirname, 'plugin_eval_expr.js'),
        path.join(__dirname, 'plugin_undo_flat_trick.js'),
        path.join(__dirname, 'plugin_undo_entries_trick.js'),
        path.join(__dirname, 'plugin_undo_concat_trick.js'),
        path.join(__dirname, 'plugin_undo_slice_trick.js'),
        path.join(__dirname, 'plugin_undo_boolean_trick.js'),
        path.join(__dirname, 'plugin_undo_fontcolor_trick.js'),
        path.join(__dirname, 'plugin_undo_italics_trick.js'),
        path.join(__dirname, 'plugin_undo_function_escape_trick.js'),
        path.join(__dirname, 'plugin_undo_escape_call.js'),
        path.join(__dirname, 'plugin_undo_function_date_trick.js'),
        path.join(__dirname, 'plugin_undo_regexp_trick.js'),
        path.join(__dirname, 'plugin_undo_string_trick.js'),
        path.join(__dirname, 'plugin_undo_number_tostring_trick.js'),
        path.join(__dirname, 'plugin_undo_object_tostring_trick.js'),
        path.join(__dirname, 'plugin_eval_return_str.js'),
        path.join(__dirname, 'plugin_eval_return_fncall.js'),
        path.join(__dirname, 'plugin_fix_eval.js'),
        path.join(__dirname, 'plugin_constructor_str.js'),
        path.join(__dirname, 'plugin_refactor_regex_constr.js'),
        path.join(__dirname, 'plugin_regex_str.js'),
        path.join(__dirname, 'plugin_simplify_false_regex.js'),
        path.join(__dirname, 'plugin_string_array_join.js'),
        path.join(__dirname, 'plugin_string_constructor_name.js'),
        path.join(__dirname, 'plugin_string_split.js'),
        path.join(__dirname, 'plugin_eval_program.js')
      ]
  });

  if (result.code == js) break;

  console.log(result.code);
  console.log("-----------------------------------------------------------------");

  js = result.code;
}

fs.writeFileSync(path.join(__dirname, output_js), js, 'utf-8');

```

Like we did manually with AST Explorer, this program modifies the input code
until it no longer changes.

As a sidenote, `undo-entries-trick` transform from earlier had to be modified
to prevent it from breaking the code:

```
-          path.replaceWith(t.stringLiteral(String(Array.prototype.entries)));
+          path.replaceWith(t.stringLiteral(String(String([]["entries"]()))));
```

Furthermore, code in `eval-return-str` transform was extended to support 
escaped characters in octal/hexadecimal form.

The following listing provides an example of debug output from deobfuscator
(most lines were removed for brevity):

```
$ node app.js examples/in1.js examples/out1.js
[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]][([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+[]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]]([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]][([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+[]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]]((!![]+[])[+!+[]]+(!![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+([][[]]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+!+[]]+([]+[])[(![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(!![]+[])[+[]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]]()[+!+[]+[!+[]+!+[]]]+((![]+[])[+!+[]]+(![]+[])[!+[]+!+[]]+(!![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+!+[]]+(!![]+[])[+[]]+[+!+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]+!+[]]+[!+[]+!+[]+!+[]+!+[]]+(!![]+[])[+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]]+[+[]]+(!![]+[])[+[]]+[!+[]+!+[]+!+[]+!+[]]+[!+[]+!+[]]+(!![]+[])[+[]]+[+!+[]]+[+!+[]]+[+[]]+(!![]+[])[+[]]+[+!+[]]+[+!+[]]+[!+[]+!+[]]+(!![]+[])[+[]]+[+!+[]]+[+!+[]]+[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+[+!+[]]+[+!+[]]+[!+[]+!+[]+!+[]+!+[]]+(!![]+[])[+[]]+[+!+[]]+[!+[]+!+[]]+[+[]]+(!![]+[])[+[]]+[+!+[]]+[!+[]+!+[]]+[+!+[]]+(!![]+[])[+[]]+[+!+[]]+[!+[]+!+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]+!+[]]+(!![]+[])[+[]]+[+!+[]]+[!+[]+!+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]+!+[]+!+[]]+(!![]+[])[+[]]+[+!+[]]+[!+[]+!+[]+!+[]]+[+[]]+(!![]+[])[+[]]+[+!+[]]+[!+[]+!+[]+!+[]]+[+!+[]]+(!![]+[])[+[]]+[+!+[]]+[!+[]+!+[]+!+[]]+[!+[]+!+[]]+(!![]+[])[+[]]+[!+[]+!+[]+!+[]+!+[]]+[+!+[]]+(!![]+[])[+[]]+[+!+[]]+[!+[]+!+[]+!+[]]+[!+[]+!+[]+!+[]+!+[]]+(!![]+[])[+[]]+[!+[]+!+[]+!+[]+!+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]+!+[]+!+[]]+(!![]+[])[+[]]+[!+[]+!+[]+!+[]+!+[]]+[+!+[]]+(!![]+[])[+[]]+[!+[]+!+[]+!+[]+!+[]]+[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+[!+[]+!+[]+!+[]+!+[]]+[!+[]+!+[]+!+[]+!+[]]+(!![]+[])[+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]]+[!+[]+!+[]]+(!![]+[])[+[]]+[+!+[]]+[+[]]+[+[]]+(!![]+[])[+[]]+[+!+[]]+[!+[]+!+[]+!+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]+!+[]]+(!![]+[])[+[]]+[+!+[]]+[!+[]+!+[]+!+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]+!+[]+!+[]]+(!![]+[])[+[]]+[+!+[]]+[!+[]+!+[]+!+[]+!+[]]+[+[]]+(!![]+[])[+[]]+[+!+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]+!+[]+!+[]]+[!+[]+!+[]+!+[]+!+[]]+(!![]+[])[+[]]+[+!+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]+!+[]+!+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]+!+[]]+(!![]+[])[+[]]+[!+[]+!+[]+!+[]+!+[]]+[!+[]+!+[]]+(!![]+[])[+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]]+[+!+[]]+(!![]+[])[+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]+!+[]+!+[]]+[!+[]+!+[]+!+[]])[(![]+[])[!+[]+!+[]+!+[]]+(+(!+[]+!+[]+[+!+[]]+[+!+[]]))[(!![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([]+[])[([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+[]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]][([][[]]+[])[+!+[]]+(![]+[])[+!+[]]+((+[])[([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+[]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]]+[])[+!+[]+[+!+[]]]+(!![]+[])[!+[]+!+[]+!+[]]]](!+[]+!+[]+!+[]+[+!+[]])[+!+[]]+(![]+[])[!+[]+!+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(!![]+[])[+[]]]((!![]+[])[+[]])[([][(!![]+[])[!+[]+!+[]+!+[]]+([][[]]+[])[+!+[]]+(!![]+[])[+[]]+(!![]+[])[+!+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(!![]+[])[!+[]+!+[]+!+[]]+(![]+[])[!+[]+!+[]+!+[]]]()+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([![]]+[][[]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]](([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]][([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+[]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]]((!![]+[])[+!+[]]+(!![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+([][[]]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+!+[]]+(![]+[+[]])[([![]]+[][[]])[+!+[]+[+[]]]+(!![]+[])[+[]]+(![]+[])[+!+[]]+(![]+[])[!+[]+!+[]]+([![]]+[][[]])[+!+[]+[+[]]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(![]+[])[!+[]+!+[]+!+[]]]()[+!+[]+[+[]]]+![]+(![]+[+[]])[([![]]+[][[]])[+!+[]+[+[]]]+(!![]+[])[+[]]+(![]+[])[+!+[]]+(![]+[])[!+[]+!+[]]+([![]]+[][[]])[+!+[]+[+[]]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(![]+[])[!+[]+!+[]+!+[]]]()[+!+[]+[+[]]])()[([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+[]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]]((![]+[+[]])[([![]]+[][[]])[+!+[]+[+[]]]+(!![]+[])[+[]]+(![]+[])[+!+[]]+(![]+[])[!+[]+!+[]]+([![]]+[][[]])[+!+[]+[+[]]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(![]+[])[!+[]+!+[]+!+[]]]()[+!+[]+[+[]]])+[])[+!+[]])+([]+[])[(![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(!![]+[])[+[]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]]()[+!+[]+[!+[]+!+[]]])())()
-----------------------------------------------------------------
PLUGIN NAME: eval-expr
FROM CODE: ![] + []
TO CODE: "false"
PLUGIN NAME: eval-expr
FROM CODE: +[]
TO CODE: 0
PLUGIN NAME: eval-expr
FROM CODE: ![] + []
TO CODE: "false"
PLUGIN NAME: eval-expr
FROM CODE: !+[] + !+[]
TO CODE: 2
PLUGIN NAME: eval-expr
FROM CODE: ![] + []
TO CODE: "false"
PLUGIN NAME: eval-expr
FROM CODE: +!+[]
TO CODE: 1
PLUGIN NAME: eval-expr
FROM CODE: !![] + []
TO CODE: "true"
PLUGIN NAME: eval-expr
FROM CODE: +[]
TO CODE: 0
PLUGIN NAME: eval-expr
FROM CODE: ![] + []
TO CODE: "false"
PLUGIN NAME: eval-expr
FROM CODE: +[]
TO CODE: 0
PLUGIN NAME: eval-expr
FROM CODE: ![] + []
TO CODE: "false"
PLUGIN NAME: eval-expr
FROM CODE: !+[] + !+[]
TO CODE: 2
PLUGIN NAME: eval-expr
FROM CODE: ![] + []
TO CODE: "false"
PLUGIN NAME: eval-expr
FROM CODE: +!+[]
TO CODE: 1
PLUGIN NAME: eval-expr
FROM CODE: !![] + []
TO CODE: "true"
PLUGIN NAME: eval-expr
FROM CODE: +[]
TO CODE: 0
PLUGIN NAME: eval-expr
FROM CODE: !+[] + !+[] + !+[]
TO CODE: 3
...
-----------------------------------------------------------------
PLUGIN NAME: undo-fontcolor-trick
FROM CODE: ""["fontcolor"]()
TO CODE: "<font color=\"undefined\"></font>"
PLUGIN NAME: constructor-str
FROM CODE: 0["constructor"]
TO CODE: "function Number() { [native code] }"
PLUGIN NAME: eval-expr
FROM CODE: "j" + "o" + "i" + "n"
TO CODE: "join"
PLUGIN NAME: undo-italics-trick
FROM CODE: "false0"["italics"]()
TO CODE: "<i>false0</i>"
PLUGIN NAME: undo-italics-trick
FROM CODE: "false0"["italics"]()
TO CODE: "<i>false0</i>"
PLUGIN NAME: undo-italics-trick
FROM CODE: "false0"["italics"]()
TO CODE: "<i>false0</i>"
PLUGIN NAME: undo-fontcolor-trick
FROM CODE: ""["fontcolor"]()
TO CODE: "<font color=\"undefined\"></font>"
[]["flat"]["constructor"]([]["flat"]["constructor"]("return" + "<font color=\"undefined\"></font>"[12] + "alert164t50t42t110t112t113t114t120t121t126t127t130t131t132t41t134t47t41t43t44t52t100t136t137t140t174t176t42t51t73"["s" + 211["to" + ""["constructor"]["na" + ("function Number() { [native code] }" + [])[11] + "e"]]("31")[1] + "l" + "i" + "t"]("t")["join"](([]["flat"]["constructor"]("return" + "<i>false0</i>"[10] + false + "<i>false0</i>"[10])()["constructor"]("<i>false0</i>"[10]) + [])[1]) + "<font color=\"undefined\"></font>"[12])())();
-----------------------------------------------------------------
PLUGIN NAME: eval-expr
FROM CODE: "<font color=\"undefined\"></font>"[12]
TO CODE: "\""
PLUGIN NAME: eval-expr
FROM CODE: "function Number() { [native code] }" + []
TO CODE: "function Number() { [native code] }"
PLUGIN NAME: eval-expr
FROM CODE: "<i>false0</i>"[10]
TO CODE: "/"
PLUGIN NAME: eval-expr
FROM CODE: "<i>false0</i>"[10]
TO CODE: "/"
PLUGIN NAME: eval-expr
FROM CODE: "<i>false0</i>"[10]
TO CODE: "/"
PLUGIN NAME: eval-expr
FROM CODE: "<font color=\"undefined\"></font>"[12]
TO CODE: "\""
[]["flat"]["constructor"]([]["flat"]["constructor"]("return" + "\"" + "alert164t50t42t110t112t113t114t120t121t126t127t130t131t132t41t134t47t41t43t44t52t100t136t137t140t174t176t42t51t73"["s" + 211["to" + ""["constructor"]["na" + "function Number() { [native code] }"[11] + "e"]]("31")[1] + "l" + "i" + "t"]("t")["join"](([]["flat"]["constructor"]("return" + "/" + false + "/")()["constructor"]("/") + [])[1]) + "\"")())();
-----------------------------------------------------------------
PLUGIN NAME: eval-expr
FROM CODE: "return" + "\""
TO CODE: "return\""
PLUGIN NAME: eval-expr
FROM CODE: "function Number() { [native code] }"[11]
TO CODE: "m"
PLUGIN NAME: eval-expr
FROM CODE: "return" + "/" + false + "/"
TO CODE: "return/false/"
[]["flat"]["constructor"]([]["flat"]["constructor"]("return\"" + "alert164t50t42t110t112t113t114t120t121t126t127t130t131t132t41t134t47t41t43t44t52t100t136t137t140t174t176t42t51t73"["s" + 211["to" + ""["constructor"]["na" + "m" + "e"]]("31")[1] + "l" + "i" + "t"]("t")["join"](([]["flat"]["constructor"]("return/false/")()["constructor"]("/") + [])[1]) + "\"")())();
-----------------------------------------------------------------
PLUGIN NAME: eval-expr
FROM CODE: "na" + "m" + "e"
TO CODE: "name"
PLUGIN NAME: simplify-false-regex
FROM CODE: []["flat"]["constructor"]("return/false/")()
TO CODE: /false/
[]["flat"]["constructor"]([]["flat"]["constructor"]("return\"" + "alert164t50t42t110t112t113t114t120t121t126t127t130t131t132t41t134t47t41t43t44t52t100t136t137t140t174t176t42t51t73"["s" + 211["to" + ""["constructor"]["name"]]("31")[1] + "l" + "i" + "t"]("t")["join"]((/false/["constructor"]("/") + [])[1]) + "\"")())();
-----------------------------------------------------------------
PLUGIN NAME: string-constructor-name
FROM CODE: ""["constructor"]["name"]
TO CODE: "String"
PLUGIN NAME: refactor-regex-constr
FROM CODE: /false/["constructor"]("/")
TO CODE: /\//
[]["flat"]["constructor"]([]["flat"]["constructor"]("return\"" + "alert164t50t42t110t112t113t114t120t121t126t127t130t131t132t41t134t47t41t43t44t52t100t136t137t140t174t176t42t51t73"["s" + 211["to" + "String"]("31")[1] + "l" + "i" + "t"]("t")["join"]((/\// + [])[1]) + "\"")())();
-----------------------------------------------------------------
PLUGIN NAME: eval-expr
FROM CODE: "to" + "String"
TO CODE: "toString"
PLUGIN NAME: regex-str
FROM CODE: /\// + []
TO CODE: "/\\//"
[]["flat"]["constructor"]([]["flat"]["constructor"]("return\"" + "alert164t50t42t110t112t113t114t120t121t126t127t130t131t132t41t134t47t41t43t44t52t100t136t137t140t174t176t42t51t73"["s" + 211["toString"]("31")[1] + "l" + "i" + "t"]("t")["join"]("/\\//"[1]) + "\"")())();
-----------------------------------------------------------------
PLUGIN NAME: undo-number-tostring-trick
FROM CODE: 211["toString"]("31")
TO CODE: "6p"
PLUGIN NAME: eval-expr
FROM CODE: "/\\//"[1]
TO CODE: "\\"
[]["flat"]["constructor"]([]["flat"]["constructor"]("return\"" + "alert164t50t42t110t112t113t114t120t121t126t127t130t131t132t41t134t47t41t43t44t52t100t136t137t140t174t176t42t51t73"["s" + "6p"[1] + "l" + "i" + "t"]("t")["join"]("\\") + "\"")())();
-----------------------------------------------------------------
PLUGIN NAME: eval-expr
FROM CODE: "6p"[1]
TO CODE: "p"
[]["flat"]["constructor"]([]["flat"]["constructor"]("return\"" + "alert164t50t42t110t112t113t114t120t121t126t127t130t131t132t41t134t47t41t43t44t52t100t136t137t140t174t176t42t51t73"["s" + "p" + "l" + "i" + "t"]("t")["join"]("\\") + "\"")())();
-----------------------------------------------------------------
PLUGIN NAME: eval-expr
FROM CODE: "s" + "p" + "l" + "i" + "t"
TO CODE: "split"
[]["flat"]["constructor"]([]["flat"]["constructor"]("return\"" + "alert164t50t42t110t112t113t114t120t121t126t127t130t131t132t41t134t47t41t43t44t52t100t136t137t140t174t176t42t51t73"["split"]("t")["join"]("\\") + "\"")())();
-----------------------------------------------------------------
PLUGIN NAME: string-split
FROM CODE: "alert164t50t42t110t112t113t114t120t121t126t127t130t131t132t41t134t47t41t43t44t52t100t136t137t140t174t176t42t51t73"["split"]("t")
TO CODE: ["aler", "164", "50", "42", "110", "112", "113", "114", "120", "121", "126", "127", "130", "131", "132", "41", "134", "47", "41", "43", "44", "52", "100", "136", "137", "140", "174", "176", "42", "51", "73"]
[]["flat"]["constructor"]([]["flat"]["constructor"]("return\"" + ["aler", "164", "50", "42", "110", "112", "113", "114", "120", "121", "126", "127", "130", "131", "132", "41", "134", "47", "41", "43", "44", "52", "100", "136", "137", "140", "174", "176", "42", "51", "73"]["join"]("\\") + "\"")())();
-----------------------------------------------------------------
PLUGIN NAME: string-array-join
FROM CODE: ["aler", "164", "50", "42", "110", "112", "113", "114", "120", "121", "126", "127", "130", "131", "132", "41", "134", "47", "41", "43", "44", "52", "100", "136", "137", "140", "174", "176", "42", "51", "73"]["join"]("\\")
TO CODE: "aler\\164\\50\\42\\110\\112\\113\\114\\120\\121\\126\\127\\130\\131\\132\\41\\134\\47\\41\\43\\44\\52\\100\\136\\137\\140\\174\\176\\42\\51\\73"
[]["flat"]["constructor"]([]["flat"]["constructor"]("return\"" + "aler\\164\\50\\42\\110\\112\\113\\114\\120\\121\\126\\127\\130\\131\\132\\41\\134\\47\\41\\43\\44\\52\\100\\136\\137\\140\\174\\176\\42\\51\\73" + "\"")())();
-----------------------------------------------------------------
PLUGIN NAME: eval-expr
FROM CODE: "return\"" + "aler\\164\\50\\42\\110\\112\\113\\114\\120\\121\\126\\127\\130\\131\\132\\41\\134\\47\\41\\43\\44\\52\\100\\136\\137\\140\\174\\176\\42\\51\\73" + "\""
TO CODE: "return\"aler\\164\\50\\42\\110\\112\\113\\114\\120\\121\\126\\127\\130\\131\\132\\41\\134\\47\\41\\43\\44\\52\\100\\136\\137\\140\\174\\176\\42\\51\\73\""
[]["flat"]["constructor"]([]["flat"]["constructor"]("return\"aler\\164\\50\\42\\110\\112\\113\\114\\120\\121\\126\\127\\130\\131\\132\\41\\134\\47\\41\\43\\44\\52\\100\\136\\137\\140\\174\\176\\42\\51\\73\"")())();
-----------------------------------------------------------------
PLUGIN NAME: fix-eval
FROM CODE: []["flat"]["constructor"]("return\"aler\\164\\50\\42\\110\\112\\113\\114\\120\\121\\126\\127\\130\\131\\132\\41\\134\\47\\41\\43\\44\\52\\100\\136\\137\\140\\174\\176\\42\\51\\73\"")
TO CODE: eval("return\"aler\\164\\50\\42\\110\\112\\113\\114\\120\\121\\126\\127\\130\\131\\132\\41\\134\\47\\41\\43\\44\\52\\100\\136\\137\\140\\174\\176\\42\\51\\73\"")
PLUGIN NAME: eval-return-str
FROM CODE: eval("return\"aler\\164\\50\\42\\110\\112\\113\\114\\120\\121\\126\\127\\130\\131\\132\\41\\134\\47\\41\\43\\44\\52\\100\\136\\137\\140\\174\\176\\42\\51\\73\"")
TO CODE: "alert(\"HJKLPQVWXYZ!\\'!#$*@^_`|~\");"
[]["flat"]["constructor"]("alert(\"HJKLPQVWXYZ!\\'!#$*@^_`|~\");")();
-----------------------------------------------------------------
PLUGIN NAME: fix-eval
FROM CODE: []["flat"]["constructor"]("alert(\"HJKLPQVWXYZ!\\'!#$*@^_`|~\");")
TO CODE: eval("alert(\"HJKLPQVWXYZ!\\'!#$*@^_`|~\");")
eval("alert(\"HJKLPQVWXYZ!\\'!#$*@^_`|~\");");
-----------------------------------------------------------------
PLUGIN NAME: eval-program
FROM CODE: eval("alert(\"HJKLPQVWXYZ!\\'!#$*@^_`|~\");");
TO CODE: alert("HJKLPQVWXYZ!\'!#$*@^_`|~");
alert("HJKLPQVWXYZ!\'!#$*@^_`|~");
-----------------------------------------------------------------
```

So the deobfuscator works for small snippets. The deobfuscated line is the same 
that I entered into JSFuck web app. However for bigger snippet there 
is a problem. During the AST traversal Babel runs out of stack space and crashes
with the the following error message on the first iteration of the loop:

```
/Users/rl/src/trickster.dev-code/jsfuck_wip/jsfuck_deobfuscator/node_modules/@babel/traverse/lib/context.js:77
  visitSingle(node, key) {
             ^

RangeError: Maximum call stack size exceeded
    at TraversalContext.visitSingle (/Users/rl/src/trickster.dev-code/jsfuck_wip/jsfuck_deobfuscator/node_modules/@babel/traverse/lib/context.js:77:14)
    at TraversalContext.visit (/Users/rl/src/trickster.dev-code/jsfuck_wip/jsfuck_deobfuscator/node_modules/@babel/traverse/lib/context.js:133:19)
    at traverseNode (/Users/rl/src/trickster.dev-code/jsfuck_wip/jsfuck_deobfuscator/node_modules/@babel/traverse/lib/traverse-node.js:24:17)
    at NodePath.visit (/Users/rl/src/trickster.dev-code/jsfuck_wip/jsfuck_deobfuscator/node_modules/@babel/traverse/lib/path/context.js:107:52)
    at TraversalContext.visitQueue (/Users/rl/src/trickster.dev-code/jsfuck_wip/jsfuck_deobfuscator/node_modules/@babel/traverse/lib/context.js:105:16)
    at TraversalContext.visitSingle (/Users/rl/src/trickster.dev-code/jsfuck_wip/jsfuck_deobfuscator/node_modules/@babel/traverse/lib/context.js:79:19)
    at TraversalContext.visit (/Users/rl/src/trickster.dev-code/jsfuck_wip/jsfuck_deobfuscator/node_modules/@babel/traverse/lib/context.js:133:19)
    at traverseNode (/Users/rl/src/trickster.dev-code/jsfuck_wip/jsfuck_deobfuscator/node_modules/@babel/traverse/lib/traverse-node.js:24:17)
    at NodePath.visit (/Users/rl/src/trickster.dev-code/jsfuck_wip/jsfuck_deobfuscator/node_modules/@babel/traverse/lib/path/context.js:107:52)
    at TraversalContext.visitQueue (/Users/rl/src/trickster.dev-code/jsfuck_wip/jsfuck_deobfuscator/node_modules/@babel/traverse/lib/context.js:105:16)

Node.js v20.1.0
```

Notice function calls repeating in the stack trace. This means that we have
recursion going on in here. JSFuck makes the AST excessively bloated 
and thus difficult to programmatically simplify with Babel. 

I think this is the final point of my JSFuck deobfuscation journey. The original
objective for doing this was to learn more about Babel and AST-level deobfuscation
and that was achieved. The current deobfuscation approach was of some success
in a way that it is able to simplify sufficiently small and simple snippets,
but ran into a fundamental limitation of Babel (if you know how to solve this -
kindly let me know). 

Does that mean JSFuck output cannot be deobfuscated? No. There are open source
examples that treat JS code as string to undo the changes that JSFuck is
making:

* [JSUNFUck](https://github.com/dnetguru/JSUNFuck) - C#/.NET program
* [jsunfuck.py](https://github.com/VeNoMouS/cloudscraper/blob/master/cloudscraper/interpreters/jsunfuck.py) file in cloudscraper Python module.
* [JSFuck Decoder](https://github.com/enkhee-Osiris/Decoder-JSFuck) - simple web app developed in vanilla JS/HTML.

[TODO: screenshots]

This is indeed an easier and better way to deal with JSFuck being used to
obfuscate client-side JavaScript code. But one cannot become stronger and 
smarter by always taking an easy way. We learned about JS type coercion and about
various weird runtime tricks that JSFuck is relying on. Martin Kleppe, the
developer of JSFuck is a smart, creative person and that shows in his work.
