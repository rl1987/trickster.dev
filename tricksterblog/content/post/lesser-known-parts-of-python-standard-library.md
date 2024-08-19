+++
author = "rl1987"
title = "Lesser known parts of Python standard library"
date = "2024-08-31"
tags = ["python"]
draft = true
+++

In this article we will explore some lesser known, but interesting and useful
corners of Python standard library.

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
into one that could be use via `with` syntax.

API reference: https://docs.python.org/3/library/contextlib.html

---

WRITEME: `decimal`, `fractions`

---

API reference: https://docs.python.org/3/library/dis.html

---

WRITEME: `graphlib`

WRITEME: `itertools`

WRITEME: `statistics`

WRITEME: `zipapp`

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
