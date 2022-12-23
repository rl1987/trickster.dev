+++
author = "rl1987"
title = "Vim is touch-typing on steroids"
date = "2022-12-31"
draft = true
tags = []
+++

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

So let's get started.

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
