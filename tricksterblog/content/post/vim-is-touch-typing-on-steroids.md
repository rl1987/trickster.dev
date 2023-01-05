+++
author = "rl1987"
title = "Vim is touch-typing on steroids"
date = "2022-12-31"
draft = true
tags = []
+++

Introduction
------------

I don't suppose I need to do much explaining on the value of touch typing for developer
productivity. Today developers gain additional productivity by using Integrated Development
Environments such as PyCharm, Xcode, Visual Studio that provide features like auto-completion,
enhanced code navigation, integration with compilers, debuggers and static analysers. All of that
does not come for free. Running heavy GUI environment can be resource intensive. For example,
Android Studio is quite infamous for making laptop fans spin like crazy. Furthermore, big
GUI apps can potentially have quite a few bugs due to their size and complexity. Before
Android Studio became an established environment to develop Android apps it was not uncommon
for Android app developers to waste a lot of time fighting the bloated, unstable mess that is (was?)
Eclipse IDE. Lastly, large GUI apps can be pain to run in server environment. The general, 
philosophical answer to all of these issues is to seek minimalism in your tooling to the
extent it is possible. It may not be very feasible to develop an iOS or Android app with no
GUI by merely using CLI tools, but if you're the intended reader of this blog you can easily
do web scraper development by writing and running all your code in terminal environment 
without any GUI tools other than web browser. 

The contents of this post are largely based on [Mastering Vim](https://learning.oreilly.com/videos/mastering-vim/9781491908334/)
course by [Damian Conway](https://en.wikipedia.org/wiki/Damian_Conway), a prominent open source
figure. As I watched the course, I took notes that hopefully will be useful to other developers
as well. Do not be turned off by the oldness of source material here. Even though the course
was released back in 2014 the Vim editor is one of the timeless classics in the realm of Unix
tooling. Many things one could learn about Vim are still applicable today and will most likely
remain applicable in year 2034.

Despite being primarily a Text User Interface (TUI) program, Vim is quite complex and has
literally thousands of commands. One does not have to know all of them to be a productive Vim
user. Furthermore, Vim has an extensive ecosystem of plugins, to the exent that Vim can be
extended almost into quite complex IDE. We will not be getting much into 
that, as the current objective is to learn the common denominator of Vim usage and develop
a skill in using Vim in it's pure form, so that if you connect via SSH into some remote Linux/Unix
server for the first time you would know exactly how to do text editing there.

So let's get started. As you launch Vim, you will be in normal mode by default, until you switch
to some other mode. The following things are applicable in the normal mode.

Normal mode commands
--------------------

To access Vim documentation system, type `:help`. This will let you browse the docs. To search
the docs, you can use `:help <keyword>`. If you're unsure of the keyword, you can type some
of the keyword and use Tab key for a list of possible completions. Furthermore, one
can search the documentation by regular expression with `:helpgrep` command, e.g. 
`:helpgrep lookahead` - no slashes needed. Use `:cnext` and `:cprev` commands to go 
next and previous search result.  If you want to skip ahead to next file, use `:cnfile` command.
To go to previous file, use `:cpfile` command.

More generally, one can use `:vimgrep` command to search for regex in files other than Vim docs,
such as your codebase. It takes a regex (with slashes this time) and one or more file names.

When using Vim help system, you will find that some words or phrases are colored differently
and/or delineated by pipe characters. These are hypelinks that can be traversed by positioning
your cursor within the bars and pressing Ctrl-]. To go back one level, one can use Ctrl-T.
To get out of help system, one can use `:q` command or type `ZZ`.

One can save a lot of time and keystrokes by learning how to navigate text efficiently. One
can navigate text in normal mode one character at a time by using arrow keys or `h` for left, 
`l` for right, `k` for up and `l` for down`. Furthermore, there are ways to perform higher-orders
motions across words, lines and greater "text objects". In some systems text can also be navigated
vertically my mouse wheel or touch pad gestures.

To find out where you are in the file one can use Ctrl-G. This will give you something like the 
following line at the bottom of your Vim UI:

```
"vim-is-touch-typing-on-steroids.md" [Modified] line 64 of 66 --96%-- col 58
```

We have file name, file state (modified with unsaved changes), current line, number of total lines,
number of current column and what percentage the current line number is from the total. Furthermore,
you can put the following line in your .vimrc file:

```
set ruler
```

This will enable slightly simpler position indication with just line and column numbers.

`w` moves to start of next word, `b` - to start of previous word, `e` - to end of next word
and `ge` to end of previous word. That accelerates your text navigation as you can use single
keystroke to move across word, not just a character. But what is a word? In Vim terminology,
word is any sequence of characters delimited by non-identifier chars (e.g. whitespace, comma).
However, there's also capital-W Words in Vim that are delimited by whitespace. So we also
have `W` command that moves to next capital-W Word and also `B`, `E` and `gE` commands that
perform equivalents to aforementioned word-level motions.

Furthemore, there are line and paragraph motion commands. `0` or `|` takes you to the start
of current line, `^` to start of first word on current line, `$` to end of the current line,
Enter to start of next line and `-` to start of previous line. One can also use `{` to move to
start of current paragraph (a continuous cluster of non-empty lines) and `}` to end of current
paragraph. This will position the cursor to the empty line just before or just after a paragraph.
If these commands are used on empty lines Vim will move the cursor accordingly to previous or next
empty line.

To move to the top of the buffer, one can use `gg`. To move to the end - `G`. To move to n-th
line, type the line number in normal mode and go `G` or `gg`. To move to a certain percentage
across the buffer, one can type number and percent sign. For example, `50%` will move your
cursor halfway through the buffer. However if you just use single `%` command it will bounce
you between some matching brackets (`{ ... }`, `( ... )`, `[ ... ]`) in your code.

One can also type a number in normal mode before a motion to do that motion a given number of
times. `lllll` can be done faster as `5l` and so on. This works on all motions commands and
many oter commands as well.

To find the next instance of word under cursor, type `\*`. For previous instance, type `#`.
You can use `:set ignorecase` command to make Vim search in case-insensitive manner. After
that is on, you can do `:set smartcase` command which will let you search in case-sensitive
way on as-needed basis. For example `/selector` would search in case-insensitive way, but
`/Selector` would be a case-sensitive search.

You can turn incremental search by launching command `:set incsearch`. It searches text as you
type it and highlights it for you (but it only moves the cursor when you hit Enter; you can
hit Escape to back off from the search).

To make Vim highlight all the search results within the current buffer one can turn on 
search highlighting by doing `:set hlsearch`. To get rid of the highlighting afterwards
one can do a `:nohlsearch` command.

Insert mode commands
--------------------

`Ctrl-Y` duplicates whats in the same column on the preceding line (one character at a time).
`Ctrl-E` does this from the next line. `Ctrl-A` inserts the last inserted text again. `Ctrl-R=`
evaluated any valid Vimscript expression (can be simple arithmetic) and insert the result. 
For example, one could type `2+2` in the prompt at the bottom, press Enter and `4` would be 
inserted.

`Ctrl-T` increases code indentation level by inserting a single Tab at the start of the line
without moving the cursor. `Ctrl-D` is the opposite - it removes a single tab from start of current
line. `Ctrl-W` deletes one word that precedes the cursor. `Ctrl-O` takes you to the normal mode
for one command.

Vim dialect of regular expressions is similar to these of sed(1) and Perl, but has some key 
differences. For example, nearly all metasyntactic characters require escaping them with 
a backslash.


