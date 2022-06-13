+++
author = "rl1987"
title = "Understanding Abstract Syntax Trees"
date = "2022-06-30"
draft = true
tags = ["security", "bug-bounties", "reversing"]
+++

First thing that happens when a program source code is parsed by compiler or interpreter
is tokenization - cutting of code into substrings that are later organised into parse tree.
However, this tree structure merely represents textual structure of the code. Further step
is syntactic analysis - an activity of converting parse tree (also known as CST - concrete
syntax tree) into another tree structure that represent logical - not textual - structure
of the program. This new tree structure that emerges from syntactic analysis is known as 
Abstract Syntax Tree (AST). AST is further processed to yield some form of executable code,
possibly with some optimizations being applies on the way.

AST represents code in terms of it's logical building blocks and their relations to each other.
Program is top most node that has nodes representing expression statements, functions calls,
variable declarations and many other things that collectively represent the code that
was parsed.

One way to see what ASTs are like is to play with [ASTExplorer](https://astexplorer.net/) web
app. For example, we can choose Python and put some Hello World example into code editor:

```python
#!/usr/bin/python3

def main():
    print("Hello world")
    
if __name__ == "__main__":
    main()
```

By exploring the AST viewer on the right hand side we can see that `main()` function is
represented by `FunctionDeclaration` node with two children: `Identifier` holding the name
for the function and `BlockStatement` at property `body` that also has `body` property with
an array holding a single `ExpressionStatement` node that points to some further descendant
nodes.

WRITEME: some examples

WRITEME: applications of ASTs outside compilers

WRITEME: significance to scraping/automation
