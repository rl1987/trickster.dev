+++
author = "rl1987"
title = "Building Python script CLIs with argparse and Click"
date = "2022-08-31"
draft = true
tags = ["python"]
+++

To make Python script parametrisable with some input data we need to develop
a Command Line Interface. This will enable the end user to run the script with
various inputs and provide a way to choose optional behaviors that the script
supports. For example, running the script with `--silent` suppresses the output
that it would otherwise print to the terminal, whereas `--verbose` makes the
output extra detailed with fine-grained technical details included. Scripts
with well developed CLIs can be invoked in a reproducible way and thus it is 
possible to integrate them into larger automation flows.

The simplest way to make Python script accept input from command line is to 
read the `sys.argv` list that is populated as the script is launched. Like in
C programs, `sys.argv[0]` is name of the program being launched, 
`sys.argv[1]` is the first argument, `sys.argv[2]` is the second one and so on.
Length of `sys.argv` list is number of argument plus one - if there's no CLI
arguments being passed into the script it will be 1.

The following trivial script exemplifies how this can be used to implement 
a very basic CLI:

```python
#!/usr/bin/python3

import sys


def main():
    if len(sys.argv) == 1:
        print("Usage:")
        print("{} <arg1> <arg2> ...".format(sys.argv[0]))
        return

    for arg in sys.argv[1:]:
        print(arg)


if __name__ == "__main__":
    main()
```

As we can see, the CLI arguments are accessed from within the script and printed to
standard output:

```
$ python3 argv_demo.py 
Usage:
argv_demo.py <arg1> <arg2> ...
$ python3 argv_demo.py 1 2 3
1
2
3
```

However this way of implementing the command line interface is fairly low-level
and under-abstracted for more advanced use cases. For example, if we wanted to
implement subcommands or multiple options that may or may not be associated with values
we would need to do quite a bit of work to parse that list of arguments into
an internal form that we would be using further in the code. 

There are some Python modules to make it easier. The argparse module ships with
vanilla Python installation. [Click](https://click.palletsprojects.com/en/8.1.x/) 
is an open source project that provides further abstraction layer to enable 
setting up the CLI with very little code.

For demonstration purposes, let us assume that we want to develop a simple
script that takes one or more HTTP(S) URLs, tries fetching them with GET
requests and prints the HTTP response status codes to the user.

