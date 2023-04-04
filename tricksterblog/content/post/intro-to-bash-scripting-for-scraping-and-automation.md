+++
author = "rl1987"
title = "Intro to Bash scripting for scraping and automation"
date = "2023-04-04"
tags = ["bash"]
+++

Bash is a Linux/UNIX program that reads users commands from the users, parses
them and executes the appropriate programs through OS-specific APIs. Since
it covers these APIs and provides some extra features on top of them this kind
of program is called a shell. Bash is not merely an interface between keyboard
and exec(2) et. al. It is also a scripting language and interpreter. 

Today we are going to explore various scripting facilities in Bash to learn
about programmable nature of this shell. The objective here is not
to give a tutorial on writing Bash scripts. Instead, I aim to show what
scripting capabilities it has and how does it fit into the broader reality,
with emphasis on scraping data and automating stuff.

The following text assumes a basic familiarity with the world of Linux/Unix 
software. 

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
$ wc -l < err.msg 
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
of some numeric operations on integers. On it's own, Bash does not even support 
floating point operations - you may need to use bc(1) or something else for 
that.

One way to perform integer arithmetic is to use built-in `expr` command (make
sure that you put whitespaces around parts of expression as otherwise it will
be treated as string):

```
$ expr 5 + 11
16
```

Another way is to use a `let` command that will assign the result to a variable:

```
$ let x=1+3
$ echo "$x"
4
$ let four=2*2
$ echo "$four"
4
```

`let` command also supports increments and shorthand (`+=` / `-=`):

```
$ let x++
$ echo "$x"
5
$ let x+=20
$ echo "$x"
25
```

We can also reference another variable in the computation:

```
$ let "y=2*x"
$ echo "$y"
10
```

Yet another way to do integer arithmetic operations is to use the double
parenthese notation:

```
$ two=$((1+1))
$ echo "$two"
2
$ (( three = two + 1 ))
$ echo "$three"
3
```

Like the `let` command, this notation also supports increments/decrements and
shorthand operations:

```
$ z=11
$ ((z++))
$ echo "$z"
12
$ ((z+=55))
$ echo "$z"
67
$ ((z--))
$ echo "$z"
66
```

To compute some floating point numbers, we can use `printf` command to generate
a command for bc(1) and read the result into variable by using a command
substitution syntax (`$( ... )`):

```
$ a=3
$ b="2.1111111111111111"
$ result=$(printf "scale=5\n%d / %f\n" "$a" "$b" | bc -l)
$ echo "$result"
1.42105
```

Bash supports basic string manipulation functionality, such as substitutions and
slicing.

For a string manipulation syntax, see the following examples:

```
$ msg="cypherpunks write code"
$ echo "${#msg}" # Get length.
22
$ echo "${msg:0:6}" # Get substring by starting index and length.
cypher
$ echo "${msg:(-4):4}" # Index can also count to count backwards from end of string.
code
$ echo "${msg%code}" # Remove suffix.
cypherpunks write 
$ echo "${msg%cypher}" # Remove prefix.
cypherpunks write code
$ echo "${msg/write/develop}" # Replace string (single match).
cypherpunks develop code
$ echo "${msg//c/C}" # Replace string (multiple matches).
Cypherpunks write Code
$ echo "${msg/%code/software}" # Replace suffix.
cypherpunks write software
$ echo "${msg/#cypher/crypto}" # Replace prefix.
cryptopunks write code
```

For conditional logic, Bash supports if-statements and `case` (switch) statements.

In simple cases, if-statements can have one line form:

```
$ if [[ 1 == 1 ]]; then echo "yes"; fi
yes
$ if [[ 1 == 2 ]]; then echo "yes"; else echo "no"; fi
no
```

Okay, so this is getting a rather dry and boring, so let's provide an example
from real world software - [Axiom](/post/axiom-just-in-time-dynamic-infra-for-offensive-security-operations/).

There are following lines of code in file 
[interact/axiom-wait](https://github.com/pry0cc/axiom/blob/master/interact/axiom-wait#L11):

```bash
if [ ! -z "$2" ]
then
    instance="$2"
fi
```

We see a bit different conditional syntax here. `$2` is the second CLI argument
to the script and here it is being checked for having a defined value. `-z`
stands for "is empty/undefined" and `!` is a logical NOT operation.

How does the `case` statement look like? We can find an example in file
[interact/axiom-scan](https://github.com/pry0cc/axiom/blob/master/interact/axiom-scan#L12):

```bash
BASEOS="$(uname)"
case $BASEOS in
'Darwin')
    PATH="$(brew --prefix coreutils)/libexec/gnubin:$PATH"
    ;;
*) ;;
esac
```

Here it reads the output of uname(1) into variable `BASEOS`. If the value is
`Darwin` is it updates the `PATH` environment variable with one more entry. 
In the default case it does nothing (see line `*) ;;`).

Like many programming languages, Bash enables iteratative code through for and
while loops.

The following example shows how for loop can be used to iterate across output
of some command, one line at a time:

```bash
i=1
for f in $(find "$tmp/split/" -type f | tr '/' ' ' | awk '{ print $NF }')
do
        instance="$(echo $instances | awk "{ print \$$i }")"
        i=$((i+1))

        mv "$tmp/split/$f" "$tmp/input/$instance"
    done
    total=$i
}
```

Example of while loop can be seen in file 
[interact/account-helpers/aws.sh](https://github.com/pry0cc/axiom/blob/641dba34424b0c8fe5afa6b8473a79cce7a39c3e/interact/account-helpers/aws.sh):

```bash
echo -e -n "${Green}Please enter your AWS Access Key ID (required): \n>> ${Color_Off}"
read ACCESS_KEY
while [[ "$ACCESS_KEY" == "" ]]; do
	echo -e "${BRed}Please provide a AWS Access KEY ID, your entry contained no input.${Color_Off}"
	echo -e -n "${Green}Please enter your token (required): \n>> ${Color_Off}"
	read ACCESS_KEY
done
```

In this case the loop would iterate until the user would provide a non-empty
input (`read` command reads text from the user and saves it into a variable).

Like many programming languages, Bash provides two basic built-in data structures:
arrays and dictionaries. 

Bash array can be declared and used as follows:

```
$ numbers=(1 2 3 4 5) # Declaring an array.
$ echo "${numbers[0]}" # Array indexing - getting an element
1
$ echo "${#numbers[@]}" # Array length
5
$ echo "${numbers[@]}" # Get all elements
1 2 3 4 5
$ numbers[0]=0 # Array indexing - setting an element
$ echo "${numbers[@]}" # Get all elements
0 2 3 4 5
$ numbers+=("six") # Append to array
```

The following listing shows how Bash dictionaries can be used in practice:

```
$ declare -A people # Declare empty dictionary.
$ people=(["John"]: "555-1212" ["Steve"]: "555-1313") # Initialise the dictionary
$ echo "${people['John']}" # Get value by key.
555-1212
$ echo "${people['Alice']}"

$ echo "${people[@]}" # Get all keys.
555-1313 555-1212
$ echo "${!people[@]}" # Get all values.
Steve John
$ for key in "${!people[@]}"; do value="${people[$key]}"; echo "$key - $value"; done # Iterate across dictionary.
Steve - 555-1313
John - 555-1212
$ people['Alice']='555-0000' # Set value for key.
$ echo "${people['Alice']}"
555-0000
```

Note, however, that Bash dictionaries are not supported in legacy (pre-4.0)
version of Bash. If you are using macOS then you may need to update your Bash
via Homebrew, as Apple does not ship modern Bash versions due to license issue.

Bash also supports functions. One example would be the following simple
function from Axiom codebase, file 
[interact/includes/system-notification.sh](https://github.com/pry0cc/axiom/blob/825570cf0387c8dc2c0489e594aa196abf71784b/interact/includes/system-notification.sh):

```bash
# method issuing notifications in place of notify-send on OSX
# expects a title as first and a notification as second argument
function notifyOSX {
  osascript -e "display notification \"$2\" with title \"$1\""
}
```

This function generates macOS system notification with title from first argument
(`$1`) and description from second argument (`$2`). It can be called as follows:

```bash
notifyOSX "Warning" "The end is near"
```

As we can see, the function call expression has the same syntax as a regular
Bash command. After, CLI is API when you're developing shell scripts.

The following CLI tools might be of interest when developing Bash scripts
in web scraping/automation/security fields:

* [xidel](https://github.com/benibela/xidel) for introducing web scraping
functionality into your script. Fetches pages and runs XPath queries or CSS
selectors for data extraction.
* [jq](https://github.com/stedolan/jq) - JSON processing tool with it's own
domain-specific language.
* [pup](https://github.com/ericchiang/pup) for running CSS selectors on HTML
pages.
* [Shellcheck](https://github.com/koalaman/shellcheck) is a shell script
static analysis tool for finding potential problems with your code. Highly
recommended, as Bash has it's own share of footguns.

We have surveyed the various features of Bash and now can consider the value
proposition that Bash brings to the table for someone doing web scraper 
development, automation engineering, bounty hunting or even old school kind
of system administration.

The way I see it, the value proposition can be viewed like this...

First, it provides a common denominator scripting language for Linux/Unix
that also serves as a power tool for users working in command line environment.
For example, instead of manually running 100 commands to import 100 CSV files
into a SQLite database you could do a quick for loop right in your shell. Due
to availability of Bash in many server and development environments this will
most likely be possible without installing any additional dependencies.

Second, Bash is a glue language for uniting multiple CLI tools into greater
workflow. For example, you may have a Scrapy project that you run through
Scrapy CLI and also some helper scripts to postprocess your data before uploading
it to some remote system. Due to Bash statements being pretty much the same as
Unix/Linux commands (with some extra features) you have a low friction way
to chain the invocations of all your tools into single flow that is launched
from a Bash script.

Axiom project demonstrates that one can develop quite extensive piece of software 
by mainly relying on Bash. However, I would not recommend doing so as there 
are better languages for this kind of work. The value of Bash scripting lies in 
introducing programmability and automation capabilities into command line
workflows.

To learn more about Bash scripting, see the following resources:

* [Bash Hackers Wiki](https://wiki.bash-hackers.org/)
* [Official Bash Manual](https://www.gnu.org/savannah-checkouts/gnu/bash/manual/bash.html)
* [Bash manpage](https://linux.die.net/man/1/bash)

