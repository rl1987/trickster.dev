+++
author = "rl1987"
title = "JavaScript AST manipulation with Babel: untangling scope confusion"
date = "2023-01-31"
draft = true
tags = ["security", "reverse-engineering", "javascript"]
+++

In computer programming, a lexical scope of an identifier (name of function, 
class, variable, constant, etc.) is area within the code where that identifier
can be used. Some identifiers have global scope meaning they can be used in the
entire program. Others have narrowed-down scope that is limited to one single
function or code block between curly braces. Identifier names can be reused
between scopes - conflict is resolved by preferring the innermost scope for a
given identifier. Lexical scopes are set in stone as the program is written.

JavaScript also has some support for dynamic scoping that is resolved during
program runtime, but let us put that aside for time being.

Introducing redundant lexical scopes with repeating identifiers is often done
for code obfuscation purposes, as it makes code hard to read and understand.
This motivates us to learn how to gain clarity when such scope obfuscation
technique is applied on client-side JavaScript code that we want to reverse 
engineer.

Since Babel parses the JS code into data model representing logical structure
of the code, it also has a capability to represent lexical scopes via `Scope`
object. Furthermore, Babel is able to handle scope bindings - relations between
identifiers and scopes. Through a scope binding we can get track the usage of
variable name or some other identifier to track down where in the code that
identifier is being referenced. Thus we have all the tools to programmatically 
disambiguate between multiple identifiers across nested scopes and convert 
the code into a more readable form.



WRITEME: toy example on ASTExplorer

WRITEME: real-worldish example on ASTExplorer

Note however that Babel does not track variables scopes across files. It can 
only work with one file at a time.
