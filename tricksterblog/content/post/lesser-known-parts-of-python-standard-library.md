+++
author = "rl1987"
title = "Lesser known parts of Python standard library"
date = "2024-08-31"
tags = ["python"]
draft = true
+++

WRITEME: `collections` 

WRITEME: `contextlib` 

WRITEME: `decimal`, `fractions`

WRITEME: `dis`

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
