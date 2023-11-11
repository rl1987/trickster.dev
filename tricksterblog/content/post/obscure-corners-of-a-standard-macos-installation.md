+++
author = "rl1987"
title = "Obscure corners of a standard macOS installation"
date = "2023-11-15"
draft = true
tags = ["macos"]
+++

Apache httpd
------------

A little known fact is that macOS ships with Apache httpd. You can launch it
by running `sudo apachectl start`. Configuration files are available in
/etc/apache2 directory and default `DocumentRoot` is /Library/WebServer/Documents.
Note however that macOS no longer ships PHP/Ruby/Perl so you will need to install
a scripting language separately to 

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

Font Book
---------

Font Book is a viewer for all the fonts installed on your macOS system that also
allows installing optional or custom fonts.

/usr/share/calendar and calendar(1)
-----------------------------------

Modern macOS is Unix system (officially and ancestrally). Many technical details
from BSD systems can be found in macOS. One example is /usr/share/calendar
directory that has human and machine readable files listing various notable 
dates, such as national holidays:

```
$ ls -lh
total 248
-rw-r--r--  1 root  wheel   483B Sep  2 10:35 calendar.all
-rw-r--r--  1 root  wheel   1.4K Sep  2 10:35 calendar.australia
-rw-r--r--  1 root  wheel    13K Sep  2 10:35 calendar.birthday
-rw-r--r--  1 root  wheel   1.0K Sep  2 10:35 calendar.christian
-rw-r--r--  1 root  wheel   3.2K Sep  2 10:35 calendar.computer
-rw-r--r--  1 root  wheel   269B Sep  2 10:35 calendar.croatian
-rw-r--r--  1 root  wheel   1.7K Sep  2 10:35 calendar.dutch
-rw-r--r--  1 root  wheel    22K Sep  2 10:35 calendar.freebsd
-rw-r--r--  1 root  wheel   265B Sep  2 10:35 calendar.french
-rw-r--r--  1 root  wheel   261B Sep  2 10:35 calendar.german
-rw-r--r--  1 root  wheel    25K Sep  2 10:35 calendar.history
-rw-r--r--  1 root  wheel    21K Sep  2 10:35 calendar.holiday
-rw-r--r--  1 root  wheel   280B Sep  2 10:35 calendar.hungarian
-rw-r--r--  1 root  wheel   6.5K Sep  2 10:35 calendar.judaic
-rw-r--r--  1 root  wheel   1.4K Sep  2 10:35 calendar.lotr
-rw-r--r--  1 root  wheel    13K Sep  2 10:35 calendar.music
-rw-r--r--  1 root  wheel   674B Sep  2 10:35 calendar.newzealand
-rw-r--r--  1 root  wheel   264B Sep  2 10:35 calendar.russian
-rw-r--r--  1 root  wheel   843B Sep  2 10:35 calendar.southafrica
-rw-r--r--  1 root  wheel   269B Sep  2 10:35 calendar.ukrainian
-rw-r--r--  1 root  wheel   1.4K Sep  2 10:35 calendar.usholiday
-rw-r--r--  1 root  wheel   469B Sep  2 10:35 calendar.world
drwxr-xr-x  3 root  wheel    96B Sep  2 10:35 de_AT.ISO_8859-15
drwxr-xr-x  9 root  wheel   288B Sep  2 10:35 de_DE.ISO8859-1
drwxr-xr-x  2 root  wheel    64B Sep  2 10:35 de_DE.ISO8859-15
drwxr-xr-x  7 root  wheel   224B Sep  2 10:35 fr_FR.ISO8859-1
drwxr-xr-x  2 root  wheel    64B Sep  2 10:35 fr_FR.ISO8859-15
drwxr-xr-x  4 root  wheel   128B Sep  2 10:35 hr_HR.ISO8859-2
drwxr-xr-x  5 root  wheel   160B Sep  2 10:35 hu_HU.ISO8859-2
drwxr-xr-x  9 root  wheel   288B Sep  2 10:35 ru_RU.KOI8-R
drwxr-xr-x  6 root  wheel   192B Sep  2 10:35 uk_UA.KOI8-U
```

For example, calendar.computer lists notable dates from computer history:

```
$ head -n 20 /usr/share/calendar/calendar.computer
/*
 * Computer
 *
 * $FreeBSD: src/usr.bin/calendar/calendars/calendar.computer,v 1.11 2007/09/07 03:23:06 edwin Exp $
 */

#ifndef _calendar_computer_
#define _calendar_computer_

01/01	AT&T officially divests its local Bell companies, 1984
01/01	The Epoch (Time 0 for UNIX systems, Midnight GMT, 1970)
01/03	Apple Computer founded, 1977
01/08	American Telephone and Telegraph loses antitrust case, 1982
01/08	Herman Hollerith patents first data processing computer, 1889
01/08	Justice Dept. drops IBM suit, 1982
01/10	First CDC 1604 delivered to Navy, 1960
01/16	Set uid bit patent issued, to Dennis Ritchie, 1979
01/17	Justice Dept. begins IBM anti-trust suit, 1969 (drops it, January 8, 1982)
01/24	DG Nova introduced, 1969
01/25	First U.S. meeting of ALGOL definition committee, 1958
```

There is also calendar(1) - a CLI tool to help you remember some notable dates
based on the calendar file (the following output is from 2023 November 10):

```
$ calendar -f /usr/share/calendar/calendar.usholiday 
Nov 11 	Veterans' Day
$ calendar -f /usr/share/calendar/calendar.world    
Nov 10 	Greg Lake is born in Bournemouth, England, 1948
Nov 10*	Parshas Toldos
Nov 10 	King's Birthday in Bhutan
Nov 10 	Henry Stanley asks David Livingston, "Dr. Livingston, I presume?", 1871
Nov 10 	Cpt. Wirz, commandant of Andersonville Prison hanged, 1865
Nov 10 	41 Women arrested in suffragette demonstrations near White House, 1917
Nov 10 	Soviet President Leonid Brezhnev dies at age 75, 1982
Nov 10 	Martin Luther born in Eisleben, Germany, 1483
Nov 11*	Rosh Chodesh Kislev (Beginning of the month of Kislev)
Nov 11 	Republic Day in Maldives
Nov 11 	Remembrance Day in Canada
Nov 11 	Independence of Cartagena in Colombia
Nov 11 	Independence Day in Angola
Nov 11 	Angola gains independence from Portugal, 1975
Nov 11 	Washington becomes the 42nd state, 1889
Nov 11 	Kurt Vonnegut, Jr, born in Indianapolis, 1922
Nov 12 	Neil Young is born in Toronto, 1945
Nov 12 	USA first exports oil to Europe, 1861
Nov 12 	Dr. Sun Yat-sen's Birthday in Taiwan
Nov 13 	Paul Simon born, 1942
Nov 13 	St. Augustine of Hippo born in Numidia, Algeria, 354
Nov 13 	Robert Louis Stevenson born, 1850
```

pbcopy(1) and pbpaste(1)
------------------------

These two tools integrate macOS pasteboard into terminal workflows. Piping
text into `pbcopy` copies it and running `pbpaste` outputs text from pasteboard
into standard output:

```
$ echo "crypto stands for cryptography" | pbcopy
$ pbpaste
crypto stands for cryptography
```

networkQuality
--------------

`networkQuality` is CLI tool to measure UL/DL bandwidth and latency of your 
network connection.
