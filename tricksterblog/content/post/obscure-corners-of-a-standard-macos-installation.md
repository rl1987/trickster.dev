+++
author = "rl1987"
title = "Obscure corners of a standard macOS installation"
date = "2023-11-10"
draft = true
tags = ["macos"]
+++

WRITEME: Apache httpd

say(1) and TTS in Edit menu
---------------------------

macOS has built-in text-to-speech capabilities. To make your Mac speak out some
text, pipe it to the say(1) program:

```
$ echo "colorless green ideas sleep furiously" | say
```

You can also pass the text as via CLI arguments:

```
$ say "hello world"
```

Running it with `-v "?"` prints a list of voices available. Multiple languages
are supported and there are some fun novelty voices. You can choose a 
voice by passing voice name through `-v`:

```
$ say "hello world" -v Bells
```

say(1) program can be used as TTS component in your shell scripts, cronjobs
or other automations.

For most of macOS GUI programs you can highlight some text on the screen and make
it spoken through Edit -> Speech -> Start Speaking.

screen(1)
---------

There's no tmux in a standard macOS install, but older equivalent of tmux - 
GNU screen - is shipped with macOS. It will be less convenient, but it still
gives you an option to make CLI tools run in the background without keeping an
active terminal session. Like tmux, it supports terminal session multiplexing
with pseudo-window manager features like splitting the terminal into multiple
panes. Read the screen(1) manpage for further information.

WRITEME: DTrace?

Grapher
-------

Grapher is a simple GUI tool to draw 2D and 3D graphs of mathematical functions.
It supports various coordinate systems such as classical, spheral, logarithmic,
cylindrical. Both regular and differential equations are supported.

Digital Colour Meter
--------------------

Digital Colour Meter is a GUI app to measure the exact RGB color values of the
pixel under the cursor. This is helpful for GUI or frontend programming tasks
that require reproducing the exact colors from the design images. Command-L 
makes it (un)lock on a point on the screen.

WRITEME: Automator and AppleScript

Font Book
---------

Font Book is a viewer for all the fonts installed on your macOS system that also
allows installing optional or custom fonts.

/usr/share/calendar
-------------------

WRITEME

WRITEME: objdump, nm?
