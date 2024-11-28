+++
author = "rl1987"
title = "Lesser known parts of Python standard library"
date = "2024-08-19"
tags = ["python"]
+++

In this article we will explore some lesser known, but interesting and useful
corners of Python standard library.

---

Python dictionaries and lists are bread and butter for many applications, but
might be too simple for more advanced data organisation. To provide more 
powerful containers for storing data in memory Python ships a `collection` 
module with things like:

* Deque - list-like data structure for efficient insertion and removal of items 
from either end.
* Counter - subclass of dictionary to count stuff.
* `ChainMap` - meta-dictionary that provides unified key-value mapping across
  multiple dictionaries without copying the data.
* Advanced structures for data mappings:
  * `OrderedDict` - dictionary that maintains order of key-value pairs (e.g. when 
    HTTP header value matters for dealing with certain security mechanisms).
  * `namedtuple` - a factory function that creates a subclass of tuple with named
    fields. Could be convenient for more OOP approach than just using `dict`.
  * `defaultdict` - dictionary with some or all or the values pre-filled. Could
    be handy when you want to provide values for fields that may be missing
    in web pages being scraped.
* `UserDict`, `UserList` and `UserString` - wrappers for `dict`, `list` and `str`
for further subclassing.

API reference: https://docs.python.org/3/library/collections.html

---

Python has `with` keyword to create context manager that will auto-cleanup 
things within lexical scope. For example, you don't have to worry about closing
a file yourself if you open it like this:

```python
with open("results.txt", "w") as out_f:
    out_f.write("...\n")
    ...
```

`contextlib` module provide helpers to work with context managers in your code.
For example, you can use `@contextmanager` annotation to turn your own function
into one that could be used via `with` syntax.

API reference: https://docs.python.org/3/library/contextlib.html

---

Due to technical reality of how floating point number are represented, 
floating point computations can have some weird results:

```
>>> 0.1 + 0.1 + 0.1 - 0.3
5.551115123125783e-17
>>> 1.2 + 2.2
3.4000000000000004
```

This is mathematically incorrect and a deal breaker for some applications, such
as those dealing with money. To address this problem, Python ships `decimal` 
module that allows us represent decimal numbers as Python objects with operator
overloading. Computations are adjusted so that we get the correct result
(within a configurable level of precision):

```
>>> from decimal import *
>>> one_point_two = Decimal('1.2')
>>> one_point_two
Decimal('1.2')
>>> two_point_two = Decimal('2.2')
>>> two_point_two
Decimal('2.2')
>>> one_point_two + two_point_two
Decimal('3.4')
```

API reference: https://docs.python.org/3/library/decimal.html

---

Likewise, we can run into problem when dealing with fractions - one third is 
not exactly equal to 0.333... Python ships with `fractions` module to represent
them as Python objects with operator overloading:


```
>>> import fractions
>>> one_third = fractions.Fraction(numerator=1, denominator=3)
>>> 2 * one_third
Fraction(2, 3)
```

API reference: https://docs.python.org/3/library/fractions.html


---

Python interpreter is implemented as [stack machine](https://en.wikipedia.org/wiki/Stack_machine)
internally. When you run some Python code it is compiled to Python-specific 
bytecode that Python VM executes. For debugging or performance optimisation 
purposes it might be desirable to disassemble Python bytecode into instruction.
The standard Python installation ships with `dis` module that takes Python
code units (e.g. a function) and disassembles the code into a kind of 
pseudo-assembler:

```
>>> import dis
>>> def add(a, b):
...     return a+b
... 
>>> dis.dis(add)
  1           0 RESUME                   0

  2           2 LOAD_FAST                0 (a)
              4 LOAD_FAST                1 (b)
              6 BINARY_OP                0 (+)
             10 RETURN_VALUE
```

API reference: https://docs.python.org/3/library/dis.html

---

Python `statistics` module provides a small toolkit of statistical algorithms
for relatively simple applications where it is an overkill to use Pandas or
Numpy: standard deviation, several kinds of average of numeric data, linear
regression, correlation, normal distribution and others. For people eager to 
join the AI/ML revolution the docs provide a sample code for making Naive 
Bayes classifier - an algorithm that can be considered a minimum viable 
example of machine learning.

API reference: https://docs.python.org/3/library/statistics.html

---

You may sometimes want to open web browser from your Python code. Since Python
is portable and multiplatform language this may be bit of hassle due to 
differences between platforms and setups. To make this easier Python ships a
`webbrowser` module with simple API to make a browser show a page. For example,
we can call `open_new()` function with URL:

```
>>> import webbrowser
>>> webbrowser.open_new('https://trickster.dev')
True
```

If you want to open a local file (e.g. HTML report with results of some 
automation) you need to pass a file URL to one of the functions:

```
>>> import os
>>> file_url = 'file://' + os.path.realpath('test.html')
>>> webbrowser.open(file_url)
True
```

API reference: https://docs.python.org/3/library/webbrowser.html

---

Distributing Python programs in source code form can be problematic if there's 
some non-technical users at the receiving end. Even if they have Python installed
there can be lacking dependencies, version conflicts and other runtime issues. 
To make this less terrible Python ships `zipapp` module with CLI tool and Python
API to package Python code into single file packages. This provides an interesting
midpoint between using virtual environments and solutions like PyInstaller to 
compile the app into platform-specific form - code remains portable, but
Python interpreter has to be there to run it.

API reference: https://docs.python.org/3/library/zipapp.html

