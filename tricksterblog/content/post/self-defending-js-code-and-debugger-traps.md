+++
author = "rl1987"
title = "Self-defending JS code and debugger traps"
date = "2023-07-02"
tags = ["security", "javascript"]
+++

Sometimes programmers really don't want their code to tampered with during runtime. 
Code obfuscation makes it harder to read and understand, but by itself does not
do anything against modification and dynamic analysis with a debugger. This is
particularly applicable to client-side JavaScript code that is meant to be 
running in web browser environment. After all, the code is largely under users
control after it is fetched from the server. We will look into two kinds of 
techniques to make this kind of tampering harder: self-defending code to hinder
code modifications and debugger traps are meant to mess with debugger if someone
tries to dynamically step through the code during runtime. Whitehat developers
at security or anti-fraud software companies would be interested in these 
techniques for the same reason as the blackhat malware writers: to hinder
their adversaries from discovering the inner working of the code and developing
attacks or defenses against it.

We can use [obfuscator.io](https://obfuscator.io/) to get simple examples of 
both techniques. Let us start with the following very basic unprotected snippet:

```javascript
// Paste your JavaScript code here
function hi() {
  console.log("Hello World!");
  console.log("Hello World!");
  console.log("Hello World!");
  console.log("Hello World!");
  console.log("Hello World!");
  console.log("Hello World!");
  console.log("Hello World!");
}
hi();
```

On the obfuscator web UI we uncheck all checkboxes except "Self Defending" and
"Compact". We get the following obfuscated snippet:

```javascript
function hi(){var _0x3298fd=(function(){var _0x3c6e04=!![];return function(_0x471481,_0x2bd7a3){var _0x14b95c=_0x3c6e04?function(){if(_0x2bd7a3){var _0xc92697=_0x2bd7a3['apply'](_0x471481,arguments);_0x2bd7a3=null;return _0xc92697;}}:function(){};_0x3c6e04=![];return _0x14b95c;};}());var _0x3a8b12=_0x3298fd(this,function(){return _0x3a8b12['toString']()['search']('(((.+)+)+)+$')['toString']()['constructor'](_0x3a8b12)['search']('(((.+)+)+)+$');});_0x3a8b12();console['log']('Hello\x20World!');console['log']('Hello\x20World!');console['log']('Hello\x20World!');console['log']('Hello\x20World!');console['log']('Hello\x20World!');console['log']('Hello\x20World!');console['log']('Hello\x20World!');}hi();
```

[Screenshot 1](/2023-07-01_13.38.21.png)

Undoing the minification makes it bit cleaner:

```javascript
function hi() {
  var _0xd9587a = (function() {
    var _0x505420 = !![];
    return function(_0x1ae0dc, _0x3c054) {
      var _0x1c2bf6 = _0x505420 ? function() {
        if (_0x3c054) {
          var _0x6b34ef = _0x3c054['apply'](_0x1ae0dc, arguments);
          _0x3c054 = null;
          return _0x6b34ef;
        }
      } : function() {};
      _0x505420 = ![];
      return _0x1c2bf6;
    };
  }());
  var _0x23cc70 = _0xd9587a(this, function() {
    return _0x23cc70['toString']()['search']('(((.+)+)+)+$')['toString']()['constructor'](_0x23cc70)['search']('(((.+)+)+)+$');
  });
  _0x23cc70();
  console['log']('Hello\x20World!');
  console['log']('Hello\x20World!');
  console['log']('Hello\x20World!');
  console['log']('Hello\x20World!');
  console['log']('Hello\x20World!');
  console['log']('Hello\x20World!');
  console['log']('Hello\x20World!');
}
hi();
```

We see some weird obfuscated code injected in here. Let us explore it a bit
with Node.JS debugger:

```
$ node inspect self_defending_edited.js
< Debugger listening on ws://127.0.0.1:9229/d6b71c95-1217-41e4-b188-e30a7a822b47
< For help, see: https://nodejs.org/en/docs/inspector
< 
< Debugger attached.
< 
 ok
Break on start in self_defending_edited.js:28
 26   console['log']('Hello\x20World!');
 27 }
>28 hi();
 29 
debug> s
break in self_defending_edited.js:2
  1 function hi() {
> 2   var _0xd9587a = (function() {
  3     var _0x505420 = !![];
  4     return function(_0x1ae0dc, _0x3c054) {
debug> s

...

debug> s
break in self_defending_edited.js:17
 15   }());
 16   var _0x23cc70 = _0xd9587a(this, function() {
>17     return _0x23cc70['toString']()['search']('(((.+)+)+)+$')['toString']()['constructor'](_0x23cc70)['search']('(((.+)+)+)+$');
 18   });
 19   _0x23cc70();
debug> exec _0x23cc70
[Function: function]
debug> exec _0x23cc70.toString()
'function() {\n' +
  '        if (_0x3c054) {\n' +
  "          var _0x6b34ef = _0x3c054['apply'](_0x1ae0dc, arguments);\n" +
  '          _0x3c054 = null;\n' +
  '          return _0x6b34ef;\n' +
  '        }\n' +
  '      }'
debug> s
debug> s
Uncaught Error [ERR_DEBUGGER_ERROR]: Can only perform operation while paused.
    at _pending.<computed> (node:internal/debugger/inspect_client:247:27)
    at Client._handleChunk (node:internal/debugger/inspect_client:214:11)
    at Socket.emit (node:events:511:28)
    at Socket.emit (node:domain:489:12)
    at addChunk (node:internal/streams/readable:332:12)
    at readableAddChunk (node:internal/streams/readable:305:9)
    at Readable.push (node:internal/streams/readable:242:10)
    at TCP.onStreamRead (node:internal/stream_base_commons:190:23)
    at TCP.callbackTrampoline (node:internal/async_hooks:130:17) {
  code: -32000
}
```

We see that it crashed when attempting to match regular expression `(((.+)+)+)+$`
on source code string of one of the nested functions. Since we undid the 
minification and introduced white space characters into the code, this operation
overwhelms the regular expression engine by causing [catastrophic
backtracking](https://stackoverflow.com/questions/64583150/how-does-javascript-self-defending-work-and-how-does-it-manage-to-enter-an-infin).

More generally, self-defending code involves self-introspection, integrity 
checking and triggering anti-tampering countermeasures. In this case the latter
two were done together in the weird regex statement, but they can be separate.
Integrity checking may involve hashing key parts of the code and checking against
a precomputed hash value. Anti-tampering countermeasures may involve throwing
an expection to crash the code or redirecting the user to error page.

To get an example of a debugger trap, we rerun the obfuscation with only a
"Debug Protection" feature being activated. 

[Screenshot 2](/2023-07-01_13.41.34.png)

We get the following snippet:

```javascript
function hi() {
    var _0x20b38b = (function () {
        var _0x36b5cf = !![];
        return function (_0x56f748, _0x5b111c) {
            var _0x37844a = _0x36b5cf ? function () {
                if (_0x5b111c) {
                    var _0x4a1f4c = _0x5b111c['apply'](_0x56f748, arguments);
                    _0x5b111c = null;
                    return _0x4a1f4c;
                }
            } : function () {
            };
            _0x36b5cf = ![];
            return _0x37844a;
        };
    }());
    (function () {
        _0x20b38b(this, function () {
            var _0x4ac2e9 = new RegExp('function\x20*\x5c(\x20*\x5c)');
            var _0x3b4dbb = new RegExp('\x5c+\x5c+\x20*(?:[a-zA-Z_$][0-9a-zA-Z_$]*)', 'i');
            var _0x43549a = _0x4c804e('init');
            if (!_0x4ac2e9['test'](_0x43549a + 'chain') || !_0x3b4dbb['test'](_0x43549a + 'input')) {
                _0x43549a('0');
            } else {
                _0x4c804e();
            }
        })();
    }());
    console['log']('Hello\x20World!');
    console['log']('Hello\x20World!');
    console['log']('Hello\x20World!');
    console['log']('Hello\x20World!');
    console['log']('Hello\x20World!');
    console['log']('Hello\x20World!');
    console['log']('Hello\x20World!');
}
hi();
function _0x4c804e(_0x203e97) {
    function _0x21f924(_0x6c4ed) {
        if (typeof _0x6c4ed === 'string') {
            return function (_0x194661) {
            }['constructor']('while\x20(true)\x20{}')['apply']('counter');
        } else {
            if (('' + _0x6c4ed / _0x6c4ed)['length'] !== 0x1 || _0x6c4ed % 0x14 === 0x0) {
                (function () {
                    return !![];
                }['constructor']('debu' + 'gger')['call']('action'));
            } else {
                (function () {
                    return ![];
                }['constructor']('debu' + 'gger')['apply']('stateObject'));
            }
        }
        _0x21f924(++_0x6c4ed);
    }
    try {
        if (_0x203e97) {
            return _0x21f924;
        } else {
            _0x21f924(0x0);
        }
    } catch (_0x5a4b0c) {
    }
}

```

The injected code is somewhat obfuscated, but we have a small snippet here and
can get an idea of what happens here. The obfuscator injected a code that 
performs a classical anti-debugging trick - invoking `debugger` JS statement
periodically. This will disrupt an attempt to step through the code one line at 
a time like in web browser dev tools panel and may even crash the entire browser
on a debugging attempt.

None of the above techniques are silver bullets against reverse engineer looking
to work out what exactly a malware sample does or how to defeat security
mechanisms of automation-hostile website. They merely make it incrementally
harder and can be dealt with by removing the injected code at AST level or even
by manually editing the source.

Further reading:

* [Awesome JavaScript Anti Debugging](https://github.com/weizman/awesome-javascript-anti-debugging)
* [JavaScript AntiDebugging Tricks](https://x-c3ll.github.io/posts/javascript-antidebugging/)
