+++
author = "rl1987"
title = "Intro to Bash scripting for scraping and automation"
date = "2023-03-31"
draft = true
tags = ["bash"]
+++

Bash is a Linux/UNIX program that reads users commands from the users, parses
them and executes the appropriate programs through OS-specific APIs. Since
it covers these APIs and provides some extra features on top of them this kind
of program is called a shell. Bash is not merely an interface between keyboard
and exec(2) et. al. It is also a scripting language and interpreter. As Bash
is available on most Unix/Linux systems it provides a common denominator
scripting language in many development and server environments.

Today we are going to explore various scripting facilities in Bash to learn
about programmable nature of this shell. The following text assumes a basic
familiarity with the world of Linux/Unix software.

In this world, each program has three communication channels available by
default:

* Standard input (file descriptor 0)
* Standard output (FD 1)
* Standard error (FD 2)

When you run a CLI program in a terminal it uses standard input to read stuff
you type into it and standard output to print text for you to read. Standard 
error is typically used for error messages and in some cases for a log output.

Use `>` to redirect standard output, `2>` to redirect standard error and `<`
to redirect standard input, as seen in the following example:

```
$ ls /etc > etc_list.txt
$ ls /notfound 2> err.msg
$ $ wc -l < err.msg 
       1
```

To daisy-chain two or more programs into pipeline such that standard output of
one program feeds into standard input of another you can use the pipe operator:

```
$ fortune | cowsay
 ____________________________ 
/ Sturgeon's Law:            \
|                            |
\ 90% of everything is crud. /
 ---------------------------- 
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
```

This entails a first baby-step towards using Bash as programming language. But 
to do programming, we need variables. We can indeed declare them in Bash:

```
$ x=1
$ echo "$x"
1
```

To declare a variable, we just did an assign statement. Note that there are no
whitespace characters around the `=` sign - Bash would not be able to correctly
parse it otherwise. To see what a value the variable has, we prepended the
variable name with a dollar sign and used an in-build `echo` command.

All variables in Bash are global to the script or user session unless declared
with a `local` keyword within a funcion (e.g. `local b=2`). Bash does not have
any real type system. Pretty much all data is treated as strings with exception
of some numeric operations on integers. Bash does not even support floating
point operations on it's own - you may need to use bc(1) or something else for 
that.

WRITEME: variables and basic computational ops

WRITEME: control flow (conditionals and loops)

WRITEME: arrays and dictionaries

WRITEME: functions

WRITEME: putting it all together - example script in scraping/automation field

WRITEME: tips and tricks