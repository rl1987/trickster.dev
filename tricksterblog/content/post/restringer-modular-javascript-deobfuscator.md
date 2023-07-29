+++
author = "rl1987"
title = "Restringer: modular JavaScript deobfuscator"
date = "2023-07-31"
draft = true
tags = ["security", "reverse-engineering", "ast", "javascript"]
+++

[Restringer](https://github.com/PerimeterX/restringer) is a modular Javascript
deobfuscation tool that attempts to autodetect and undo some common JS
obfuscation techniques. This tool was developed by PerimeterX for malware
analysis purposes. Besides CLI tool and a NPM module (for custom deobfuscator
development), Restringer is also available as [web app](https://restringer.tech/). 
We will be taking a look into the inner working of this tool for educational
purposes.

The underlying data model that Restringer operates on is not based on Babel
flavour of Abstract Syntax Tree. Instead, it uses a library called
[flAST](https://github.com/PerimeterX/flast) (also developed by PerimeterX)
to parse the code into *flattened* form of AST, modify it and regenerate the
code. AST flattening is a key concept in the Restringer project. Unlike in Babel,
ASTs are not represented as tree structures with references between nodes.
Instead, it is represented as an array of nodes that point to related nodes
via references:

```
$ node
Welcome to Node.js v20.4.0.
Type ".help" for more information.
> const {generateFlatAST} = require('flast');
undefined
> const ast = generateFlatAST(`console.log(1 + 2 + 3);`);
undefined
> ast
[
  <ref *1> Node {
    type: 'Program',
    start: 0,
    end: 23,
    range: [ 0, 23 ],
    body: [ [Node] ],
    sourceType: 'module',
    comments: [],
    srcClosure: [Function (anonymous)],
    nodeId: 0,
    childNodes: [ [Node] ],
    parentNode: null,
    parentKey: '',
    lineage: [],
    isScopeBlock: true,
    allScopes: { '0': [GlobalScope] },
    scope: <ref *2> GlobalScope {
      type: 'global',
      set: Map(0) {},
      taints: Map(0) {},
      dynamic: true,
      block: [Circular *1],
      through: [Array],
      variables: [],
      references: [Array],
      variableScope: [Circular *2],
      functionExpressionScope: false,
      directCallToEvalScope: false,
      thisFound: false,
      __left: null,
      upper: null,
      isStrict: false,
      childScopes: [],
      __declaredVariables: [WeakMap],
      implicit: [Object]
    }
  },
  <ref *3> Node {
    type: 'ExpressionStatement',
    start: 0,
    end: 23,
    range: [ 0, 23 ],
    expression: Node {
      type: 'CallExpression',
      start: 0,
      end: 22,
      range: [Array],
      callee: [Node],
      arguments: [Array],
      optional: false,
      nodeId: 2,
      childNodes: [Array],
      parentNode: [Circular *3],
      parentKey: 'expression',
      lineage: [Array],
      scope: [GlobalScope]
    },
    ...
  <ref *12> Node {
    type: 'Literal',
    start: 20,
    end: 21,
    range: [ 20, 21 ],
    value: 3,
    raw: '3',
    nodeId: 10,
    childNodes: [],
    parentNode: <ref *8> Node {
      type: 'BinaryExpression',
      start: 12,
      end: 21,
      range: [Array],
      left: [Node],
      operator: '+',
      right: [Circular *12],
      nodeId: 6,
      childNodes: [Array],
      parentNode: [Node],
      parentKey: 'arguments',
      lineage: [Array],
      scope: [GlobalScope]
    },
    parentKey: 'right',
    lineage: [ 0, 1, 2, 6 ],
    scope: <ref *2> GlobalScope {
      type: 'global',
      set: Map(0) {},
      taints: Map(0) {},
      dynamic: true,
      block: [Node],
      through: [Array],
      variables: [],
      references: [Array],
      variableScope: [Circular *2],
      functionExpressionScope: false,
      directCallToEvalScope: false,
      thisFound: false,
      __left: null,
      upper: null,
      isStrict: false,
      childScopes: [],
      __declaredVariables: [WeakMap],
      implicit: [Object]
    }
  }
]
```

Furthermore, flAST data model tracks variable scopes to associate symbol 
declarations with their uses.

To let us modify the code in this flat AST form, flAST provides us with another
abstraction - the `Arborist` object. There are two steps to making a code
change with flAST - we first mark the nodes we want to replace or delete,
then call `applyChanges()` method. The README file provides a simple
example:

```javascript
const {generateFlatAST, generateCode, Arborist} = require('flast');
const ast = generateFlatAST(`console.log('Hello' + ' ' + 'there!');`);
const replacements = {
  'Hello': 'General',
  'there!': 'Kenobi',
};
const arborist = new Arborist(ast);
// Mark all relevant nodes for replacement.
ast.filter(n => n.type === 'Literal' && replacements[n.value]).forEach(n => arborist.markNode(n, {
  type: 'Literal',
  value: replacements[n.value],
  raw: `'${replacements[n.value]}'`,
}));
const numberOfChangesMade = arborist.applyChanges();
console.log(generateCode(arborist.ast[0]));  // console.log('General' + ' ' + 'Kenobi');
```

Note the key conceptual difference in how the code modification is done here vs.
in Babel-based code: instead of traversing the AST recursively and applying the 
visitor function we would need to use an `filter()` API that is based on a 
functional programming approach. 

Another library that Restringer depends on is
[Obfuscation Detector](https://github.com/PerimeterX/obfuscation-detector/tree/main) - 
also from PerimeterX. This library applies pattern matching on flattened ASTs 
to detect several obfuscation techniques. For example,
[src/detectors/arrayReplacements.js](https://github.com/PerimeterX/obfuscation-detector/blob/main/src/detectors/arrayReplacements.js) file
contains the following code to detect [string array mapping](/post/javascript-ast-manipulation-with-babel-defeating-string-array-mapping/):

```javascript
const {
	arrayHasMinimumRequiredReferences,
	findArrayDeclarationCandidates,
} = require(__dirname + '/sharedDetectionMethods');

const obfuscationName = 'array_replacements';

/**
 * Array Replacements obfuscation type has the following characteristics:
 * - An array (A) is with many strings is defined.
 * - There are many member expression references where the object is array A.
 *
 * @param {ASTNode[]} flatTree
 * @return {string} The obfuscation name if detected; empty string otherwise.
 */
function detectArrayReplacements(flatTree) {
	const candidates = findArrayDeclarationCandidates(flatTree);

	for (const c of candidates) {
		const refs = c.id.references.map(n => n.parentNode);
		if (arrayHasMinimumRequiredReferences(refs, c.id.name, flatTree)) return obfuscationName;
	}
	return '';
}

module.exports = detectArrayReplacements;
```

`detectArrayReplacements()` is a detector function that relies on two other
functions: `findArrayDeclarationCandidates` and `arrayHasMinimumRequiredReferences`
from [sharedDetectionMethods.js](https://github.com/PerimeterX/obfuscation-detector/blob/main/src/detectors/sharedDetectionMethods.js)
file. The former is looking for the array expressions that look like they are 
used to do string array mapping by applying some checks within predicate of
a `filter()` call:

```javascript
/**
 * @param {ASTNode[]} flatTree
 * @return {ASTNode[]} Candidates matching the target profile of an array with more than a few items, all literals.
 */
function findArrayDeclarationCandidates(flatTree) {
	return flatTree.filter(n =>
		n.type === 'VariableDeclarator' &&
		n?.init?.type === 'ArrayExpression' &&
		arrayHasMeaningfulContentLength(n.init.elements, flatTree) &&
		!n.init.elements.some(el => el.type !== 'Literal'));
}
```

Let us unpack the predicate here. First, it checks if node type is `VariableDeclarator`.
Then, it checks if node points to another node of type `ArrayExpression` at it's
`init` property. Next, it calls `arrayHasMeaningfulContentLength()` function
to check if array length is at least 2% of the entire flat AST. Lastly, it 
performs a check to reject array that contain members that are not literals.

The other function, `arrayHasMinimumRequiredReferences()` checks for high
enough reference count to array in question:

```javascript
/**
 * @param {ASTNode[]} references
 * @param {string} targetArrayName
 * @param {ASTNode[]} flatTree
 * @return {boolean} true if the target array has at least the minimum required references; false otherwise.
 */
function arrayHasMinimumRequiredReferences(references, targetArrayName, flatTree) {
	return references.filter(n =>
		n.type === 'MemberExpression' &&
		n.object.name === targetArrayName).length / flatTree.length * 100 >= minMeaningfulPercentageOfReferences;
}
```

So if a candidate array has above 2% 
(`const minMeaningfulPercentageOfReferences = 2; // 2%`) of it's members 
referenced via member expressions, the detector function consider it to be used 
for string array mapping.


