+++
author = "rl1987"
title = "Vim is touch-typing on steroids"
date = "2023-01-31"
draft = true
tags = ["vim", "productivity"]
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

We can also run a command like `:s/<pattern>/<replacement>/` to find a pattern (could be 
regular expression) and replace it with another pattern within the current line. There 
are some variations to this command:

* `:10,33s/from/to/` - apply search and substitution across a specific range of lines (e.g.
from 10th to 33rd line).
* `:1s/from/to/` - do it on a specific line with given line number
* `-10,+33s/from/to/` - line range can also be relative to the current line number
* `-10;+33s/from/to/` - if you use semicolon between numbers, the second number will be
relative not to the current line number, but to the first line number in the range
* Metacharacters can also be used in ranges: `.` means first line, `$` means the last one
and so forth.
* `:%s/from/to/` (or `:1,$s/from/to`) does the substitution across the entire file.

You can also use patterns to specify ranges based on text content. For example, `/<pat>`/
in the beginning of command tells Vim to do substitution on next line that matches the given
pattern. `?<pat>` tells it to work on only the previous line that matches a pattern. This 
can be combined to narrow down the substitution only to specific part of source code in the
file being edited (e.g. HTML body). This also works with offsets. For example:
`?foo?+1,$-10s/<pattern>/<replacement>/' does the subsitutions from the line after previous
instance of `foo` to 10 lines before end of file. 

The above commands will only do the substitution once, but typically you want it done multiple
times (e.g. across the entire file). To achieve this, append the `/g` (global) modifier, e.g.
`s/from/to/g`. If you're unsure about replacing stuff all the time, you may want to use `/c`
modifier, e.g. `%s/cat/feline/gc`. This will let you use an interactive flow of approving or
rejecting every substitution. 

To repeat the last substitution one more time, you can press `&` or `:s` and Enter. To repeat
it globally, use `%s<Enter>`.

Beyond search-and-replace, many Vim commands also take ranges and support the above range syntax.
Thus it is valuable to learn them in order to be productive with Vim.

Sometimes you want to match lines according to some regex or pattern across the entire file,
but want to do something else than replacing text. This can be done with `:global` (or `:g`)
command. It lets you match some lines according to a pattern and run another colon command
across the matching lines. Some examples:

* `:g /^\s/ :center` - centering only the lines that are already indented (start with a space
character).
* `:g! /^\s/ :center` - center only lines that are NOT indented.
* `:g /<ISBN>/ :normal gUU` - run a normal mode command (convert all lines containing `<ISBN>`
to upper-case).`
* `:g /./ :.;/^$/join` - convert all paragraphs into a single line to make the text less messy
if it was copy-pasted in MS Word or something. Note that we use a range `.;/^$/` in a colon 
command being invoked:
  * `.` - match non-empty line
  * `;` - make the second part of the range relative to first one
  * `/^$/` - regex to match empty line, closing the range to only have non-empty lines from
    the start of paragraph.
* `:g /./ :.;/^\$/-1join` - same as above, but leaves the empty lines for readability.

This is quite powerful and can support various advanced text editing use cases.

Yanking is Vim term for copying some text and putting means pasting the text. `yy` or `Y`
yanks the current line. `yw` and `y}` yanks a word and paragraph respectively (from the
current position). More generally, `y` can be followed by any valid motion. For example,
`y$` copies text until end of line and `y/__END__` copies it until first occurence of give
pattern (`__END__` in this case). This works well with incremental search, as you would
get an indication of where the copied part would end. 

We can also use text object specification with this command. For example, to copy the entire 
word under the cursor, we say `yaw` (or `yaW` for capital-W Word). Likewise, `yas` copies
entire sentence and `yap` does the same for entire paragraph that the cursor is in.

For code editing, Vim lets you yank delimited portions of it:

* `yab` or `ya{` for curly-brace delimited block
* `ya[` for `[ ... ]`
* `ya(` for `( ... )`
* `ya<` for `< ... >`
* `ya"` for double-quoted text
* `ya'` for single-quoted text

`p` command is for pasting (putting) the text that was yanked.

To undo the last buffer change, use `u` command. To re-do it, use Ctrl-R. These can be done 
multiple times. Think of it as timeline of changes. Since Vim version 7 this timeline
can be branched. `g-` would switch to previous branch and `g+` switches to next version
of history.

Furthemore, one can "time-travel" in the text change history by using `:earlier` and `:later`
commands with time offset. For example, `:earlier 10m` takes you to buffer state that
was 10 minutes ago and `:later 30s` fast-forwards it to what it was 30 seconds later from
that time. So if you remember that your code was fine 10 minutes ago, you can go back to what 
it was back then and either discard the changes you did or move a bit forward in the history
to keep some of your work.

However, all of this change is history is discarded when you quit Vim. However, Vim 7.3 introduced
a feature of persistent undo history that can be enabled by putting the following lines
in your .vimrc file:

```
if has('persistent_undo')
    set undofile
endif
```

This will make Vim create a history file in each directory being edited. To consolidate
all the edit histories in a single directory somewhere, set `undodir` in your .vimrc. 
By default, Vim wil remember 1000 levels of changes. You can set `undolevel` to customise
this amount.

Vim also keeps track of you command history. If you want to rerun a colon command you 
can type `:` and use up and down keys to navigate the history until you find the command
that you want to repeat. You can also type the initial few characters of your command
to narrow it down. Furthermore, you can use autocompletion with Tab key when typing
your colon commands. This works with commands, file names, command arguments and so forth -
pretty much all Vim knows about can be autocompleted.

Insert mode commands
--------------------

`Ctrl-Y` duplicates whats in the same column on the preceding line (one character at a time).
`Ctrl-E` does this from the next line. `Ctrl-A` inserts the last inserted text again. `Ctrl-R=`
evaluated any valid Vimscript expression (can be simple arithmetic) and insert the result. 
For example, one could type `2+2` in the prompt at the bottom, press Enter and `4` would be 
inserted.

`Ctrl-T` increases code indentation level by inserting a single Tab at the start of the line
without moving the cursor. `Ctrl-D` is the opposite - it removes a single tab from start of 
current line. `Ctrl-W` deletes one word that precedes the cursor. `Ctrl-O` takes you to the 
normal mode for one command.

Vim dialect of regular expressions is similar to these of sed(1) and Perl, but has some key 
differences. For example, nearly all metasyntactic characters require escaping them with 
a backslash.

Typing everything in it's entirety is quite a pain and one of major arguments for using an
IDE. However, can also do auto-completion in insert mode. One could type some of the word 
and press Ctrl-X to enter completion. Next, you use another key combination to indicate what 
kind of completion you want. For example, Ctrl-X Ctrl-F is for autocompleting file names 
and file paths.  Doing this will present a pop-up with all possible completions that you 
can choose from.

Ctrl-X Ctrl-D completes a C preprocessor macro by default, but you can set `define` to
any regular expression to use it for other things. But that's a bit of pain.

Ctrl-X Ctrl-N does identifier completion that works across all sequences of keyword
characters across the current edit session. One can edit `iskeyword` option to change what
it considers a keyword character.

Ctrl-X Ctrl-I is for C and C++ programming. It works like the regular identifier completion,
but also goes into source code files that were `#include`d.

Ctrl-X Ctrl-O is a smart, unified "omni-completion" that tries to use some heuristics
to present some options to you in a smart, automatic way that is informed by the context
of where you are in the code that you are editing. This typically requires a completion
specification (some are included in the standard installation - see `:help compl-omni-filetypes`).
Furthermore, one may need to preprocess the source code with a tool called
[Exuberant ctags](https://ctags.sourceforge.net). You may also want to enable file type
detection by doing `:filetype plugin on`.

Visual modes
------------

When you type `v` Vim enters the visual mode. As you move your cursor around, it will hightlight
the text and select it. Once you have selected the exact text you want, you can run a normal
mode command and it will apply to that portion of text. That the basic visual mode.

There's also visual line mode that entails selecting entire lines. You can enter it by typing
capital `V` in the normal mode (or in basic visual mode if you want to switch).

Lastly, there' visual block mode for selecting a rectangular block to deal with something like
ASCII art tables. It can be entered by typing Ctrl-V. 
