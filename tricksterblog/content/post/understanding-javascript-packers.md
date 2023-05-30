+++
author = "rl1987"
title = "Understanding JavaScript packers"
date = "2023-05-30"
draft = true
tags = ["security", "reverse-engineering", "javascript"]
+++

In the world of desktop software, the concept of packer is not new. A packer is 
a tool that takes a binary executable file as input, applies transformations
(e.g. compression, encryption, introducing anti-debugging tricks) and outputs a
new, modified executable file that is different at binary level, but retains the
functionality of original program. Some packers, like [UPX](https://upx.github.io/)
are only meant to make the executable binaries smaller. More advanced packers
apply machine code encryption to make reverse engineering harder. The key to 
decrypt the machine code is hidden in a binary file and applied automatically 
when program is launched, but the encryption layer introduces a barrier for
disassebling or decompiling the machine code, which increases the effort 
needed to reverse engineer the inner workings of a program.

But that's old news. Nowadays a lot of software is web-based. But the thing is,
the concept of packer is also applicable in JavaScript world. There are tools
and techniques to transform JS code in such a way that it becomes smaller and/or
less readable. Thus JS packing can be used as obfuscation technique. Note that
I am not talking about simple code minification here. Instead, we're going to 
see some techniques that are similar to executable packing from the compiled 
software world.

Depending on what kind of hat the programmer is wearing, there might be different
motivations to apply JS packing. One is simply to make JS code smaller, which
helps performance. Lighter pages load faster, which leads to better user
experience and may have a positive impact on search engine ranking. JS packing
can also be applied to make things harder for web scraper developers, esp. if
there's some non-trivial client side functionality involved. For instance,
Imperva (formely known as Incapsula) antibot solution is known to have used 
[a simple JS packing technique](https://nerodesu017.github.io/antibots/programming/2021/05/07/antibots-part-3.html)
as one layer of JS SDK code obfuscation. On the black hat side, JS packing is 
used to evade detection of malicious code that is placed on compromised or 
fraudulent websites for cybercrime purposes.

There are two aspects to JavaScript packing:

1. Transforming the original code into a new (e.g. compressed, encoded, encrypted)
form. This will be hardcoded into output code.
2. Introducing a small amount of helper code that will unpack and execute the 
original code.

`eval(unescape())` is the minimum viable JS packing technique. Original code
is converted into URL-encoded form, then put as an argument to `eval(unescape())`
functions calls. 

To find an example, we can [search for `"eval(unescape("` on PublicWWW](https://publicwww.com/websites/%22eval%28unescape%28%22/).
On one of the pages we find, there's a following JS snippet:

```javascript
var myText = 'Пишите нам'; eval(unescape('%64%6f%63%75%6d%65%6e%74%2e%77%72%69%74%65%28%27%3c%61%20%68%72%65%66%3d%22%6d%61%69%6c%74%6f%3a%76%69%74%40%61%75%64%69%74%2d%69%74%2e%72%75%3f%73%75%62%6a%65%63%74%3d%25%44%30%25%41%31%25%44%30%25%42%31%25%44%30%25%42%35%25%44%31%25%38%30%25%44%30%25%42%45%25%44%30%25%42%43%25%44%30%25%42%35%25%44%31%25%38%32%25%44%31%25%38%30%22%3e%27%2b%28%6d%79%54%65%78%74%20%3f%20%6d%79%54%65%78%74%20%3a%20%27%76%69%74%40%61%75%64%69%74%2d%69%74%2e%72%75%27%29%2b%27%3c%2f%61%3e%27%29%3b'))
```

We can trivially recover the original source code of this snippet by copy-pasting
the `unescape()` call into JS REPL:

```
$ node
Welcome to Node.js v20.1.0.
Type ".help" for more information.
> unescape('%64%6f%63%75%6d%65%6e%74%2e%77%72%69%74%65%28%27%3c%61%20%68%72%65%66%3d%22%6d%61%69%6c%74%6f%3a%76%69%74%40%61%75%64%69%74%2d%69%74%2e%72%75%3f%73%75%62%6a%65%63%74%3d%25%44%30%25%41%31%25%44%30%25%42%31%25%44%30%25%42%35%25%44%31%25%38%30%25%44%30%25%42%45%25%44%30%25%42%43%25%44%30%25%42%35%25%44%31%25%38%32%25%44%31%25%38%30%22%3e%27%2b%28%6d%79%54%65%78%74%20%3f%20%6d%79%54%65%78%74%20%3a%20%27%76%69%74%40%61%75%64%69%74%2d%69%74%2e%72%75%27%29%2b%27%3c%2f%61%3e%27%29%3b')
`document.write('<a href="mailto:[REDACTED]?subject=%D0%A1%D0%B1%D0%B5%D1%80%D0%BE%D0%BC%D0%B5%D1%82%D1%80">'+(myText ? myText : '[REDACTED]')+'</a>');`
```

This turned out to be a simple trick to hide owner's email address from web
scrapers that don't execute JavaScript and are not tailored to this specific
site. 

A more complex example would be [Dean Edwards packer](http://dean.edwards.name/packer/).
Let us pack the following JavaScript snippet:

```javascript
let hello = "hello world";
console.log(hello);
```

After checking both checkboxes and pressing "Pack" button we get the following
packed code:

```javascript
eval(function(p,a,c,k,e,r){e=String;if(!''.replace(/^/,String)){while(c--)r[c]=k[c]||c;k=[function(e){return r[e]}];e=function(){return'\\w+'};c=1};while(c--)if(k[c])p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c]);return p}('1 0="0 2";3.4(0);',5,5,'hello|let|world|console|log'.split('|'),0,{}))
```

Using Beautifier.io to prettify (but not unpack at the moment - make sure all 
checkboxes are unchecked) this code makes it slightly more readable:

```javascript
eval(function(p, a, c, k, e, r) {
    e = String;
    if(!''.replace(/^/, String)) {
        while(c--) r[c] = k[c] || c;
        k = [function(e) {
            return r[e]
        }];
        e = function() {
            return '\\w+'
        };
        c = 1
    };
    while(c--)
        if(k[c]) p = p.replace(new RegExp('\\b' + e(c) + '\\b', 'g'), k[c]);
    return p
}('1 0="0 2";3.4(0);', 5, 5, 'hello|let|world|console|log'.split('|'), 0, {}))
```

In the outermost layer we see that `eval()` function is called with a value 
returned by immediately invoked function with five parameters - `p`, `a`, `c`,
`k`, `e` and `r`. The values for these arguments are related to original code
snippet and in aggregate represent a packed representation. The innermost 
function applies some regular expression magic to regenerate what the code 
was originally, so that `eval()` could execute it.

Like with the previous example, we can skip the `eval()` part and perform only
the unpacking:

```
> let unpack = function(p,a,c,k,e,r){e=String;if(!''.replace(/^/,String)){while(c--)r[c]=k[c]||c;k=[function(e){return r[e]}];e=function(){return'\\w+'};c=1};while(c--)if(k[c])p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c]);return p};
undefined
> unpack('1 0="0 2";3.4(0);',5,5,'hello|let|world|console|log'.split('|'),0,{});
'let hello="hello world";console.log(hello);'
```

We got the original code without newline in the middle. Like with other 
obfuscation techniques, we are not necessarily able to recover the exact
original code when reverse engineering.

A lot of the online JS packer tools are some variations of Dean Edwards packer
that was originally developed in C#. Thus it is useful to know how to revert
what it does to the code.

