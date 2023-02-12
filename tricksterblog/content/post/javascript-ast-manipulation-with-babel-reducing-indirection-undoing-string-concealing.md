+++
author = "rl1987"
title = "JavaScript AST manipulation with Babel: reducing indirection, undoing string concealing"
date = "2023-02-12"
draft = true
tags = ["security", "reverse-engineering", "javascript"]
+++

String concealing is a code obfuscation technique that involves some sort of
string constant recomputation (e.g. Base64 encoding or encryption with symmetric 
ciphers) being introduced into code. Furthermore, obfuscation solutions may 
introduce some variable and function indirection to further thwart reverse
engineering. In this post we will be learning how to deal with both of these
obstacles on the way to untold riches.

Let us consider the following JS snippet that we are going to obfuscate with
[obfuscator.io](https://obfuscator.io):

```javascript
(async () => {
  try {
    const response = await fetch('https://api.nike.com/cic/browse/v2?queryid=products&anonymousId=A7CA2A92E0F04E570767C7810552BBC5&country=au&endpoint=%2Fproduct_feed%2Frollup_threads%2Fv2%3Ffilter%3Dmarketplace(AU)%26filter%3Dlanguage(en-GB)%26filter%3DemployeePrice(true)%26filter%3DattributeIds(8529ff38-7de8-4f69-973c-9fdbfb102ed2%2C16633190-45e5-4830-a068-232ac7aea82c)%26anchor%3D24%26consumerChannelId%3Dd9a5bc42-4b9c-4976-858a-f159cf99c647%26count%3D24&language=en-GB&localizedRangeStr=%7BlowestPrice%7D%E2%80%94%7BhighestPrice%7D', {
      headers: {
        'authority': 'api.nike.com',
        'accept': '*/*',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'cache-control': 'no-cache',
        'origin': 'https://www.nike.com',
        'pragma': 'no-cache',
        'referer': 'https://www.nike.com/',
        'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
      }
    });
    const json = await response.json()
    console.log(json);
  } catch (error) {
    console.log(error);
  }
})();

```

Our objective is to obfuscate this code with "String Array", "String Array
Calls Tranform" and "String Array Encoding" options, then do AST-level
transformation to undo the obfuscation and get the code as close as possible
to what we started with.

[Screenshot 1](/2023-02-11_14.33.44.png)

Obfuscation tool converts the above snippet into this:

```javascript
function _0x5d79() {
    const _0x3d5a8f = [
        'yxbPlM5PA2uUy29T',
        'kI8Q',
        'zw4Tr0iSzw4Tvvm7Ct0WlJKSzw47Ct0WlJG',
        'Ahr0Chm6lY93D3CUBMLRzs5JB20',
        'Ahr0Chm6lY93D3CUBMLRzs5JB20V',
        'iM1Hy09tiG',
        'zw1WDhK',
        'y29YCW',
        'ANnVBG',
        'Bg9N'
    ];
    _0x5d79 = function () {
        return _0x3d5a8f;
    };
    return _0x5d79();
}
function _0x4ad0(_0x5d79db, _0x4ad0a1) {
    const _0x150e0f = _0x5d79();
    _0x4ad0 = function (_0x2ee979, _0x4a74f2) {
        _0x2ee979 = _0x2ee979 - 0x0;
        let _0x299466 = _0x150e0f[_0x2ee979];
        if (_0x4ad0['sjCySo'] === undefined) {
            var _0x1cb49b = function (_0x307ab8) {
                const _0x4d32cc = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/=';
                let _0x19f00a = '';
                let _0xf75b57 = '';
                for (let _0x1806d0 = 0x0, _0x425bd6, _0x1bc5e5, _0x152116 = 0x0; _0x1bc5e5 = _0x307ab8['charAt'](_0x152116++); ~_0x1bc5e5 && (_0x425bd6 = _0x1806d0 % 0x4 ? _0x425bd6 * 0x40 + _0x1bc5e5 : _0x1bc5e5, _0x1806d0++ % 0x4) ? _0x19f00a += String['fromCharCode'](0xff & _0x425bd6 >> (-0x2 * _0x1806d0 & 0x6)) : 0x0) {
                    _0x1bc5e5 = _0x4d32cc['indexOf'](_0x1bc5e5);
                }
                for (let _0x4858d8 = 0x0, _0x24c07d = _0x19f00a['length']; _0x4858d8 < _0x24c07d; _0x4858d8++) {
                    _0xf75b57 += '%' + ('00' + _0x19f00a['charCodeAt'](_0x4858d8)['toString'](0x10))['slice'](-0x2);
                }
                return decodeURIComponent(_0xf75b57);
            };
            _0x4ad0['rQzPwo'] = _0x1cb49b;
            _0x5d79db = arguments;
            _0x4ad0['sjCySo'] = !![];
        }
        const _0x29a87a = _0x150e0f[0x0];
        const _0x23768c = _0x2ee979 + _0x29a87a;
        const _0x1499a9 = _0x5d79db[_0x23768c];
        if (!_0x1499a9) {
            _0x299466 = _0x4ad0['rQzPwo'](_0x299466);
            _0x5d79db[_0x23768c] = _0x299466;
        } else {
            _0x299466 = _0x1499a9;
        }
        return _0x299466;
    };
    return _0x4ad0(_0x5d79db, _0x4ad0a1);
}
((async () => {
    const _0xdc848 = {
        _0x3da25d: 0x0,
        _0x3544fd: 0x1,
        _0x1e529f: 0x2,
        _0xc4fc60: 0x3,
        _0x16f93c: 0x4,
        _0x58c8a8: 0x5,
        _0x449635: 0x6,
        _0x2fa582: 0x7,
        _0x2e8261: 0x8,
        _0x56169a: 0x9
    };
    const _0x15ca68 = _0x4ad0;
    try {
        const _0x23768c = await fetch('https://api.nike.com/cic/browse/v2?queryid=products&anonymousId=A7CA2A92E0F04E570767C7810552BBC5&country=au&endpoint=%2Fproduct_feed%2Frollup_threads%2Fv2%3Ffilter%3Dmarketplace(AU)%26filter%3Dlanguage(en-GB)%26filter%3DemployeePrice(true)%26filter%3DattributeIds(8529ff38-7de8-4f69-973c-9fdbfb102ed2%2C16633190-45e5-4830-a068-232ac7aea82c)%26anchor%3D24%26consumerChannelId%3Dd9a5bc42-4b9c-4976-858a-f159cf99c647%26count%3D24&language=en-GB&localizedRangeStr=%7BlowestPrice%7D%E2%80%94%7BhighestPrice%7D', {
            'headers': {
                'authority': _0x15ca68(_0xdc848._0x3da25d),
                'accept': _0x15ca68(_0xdc848._0x3544fd),
                'accept-language': _0x15ca68(_0xdc848._0x1e529f),
                'cache-control': 'no-cache',
                'origin': _0x15ca68(_0xdc848._0xc4fc60),
                'pragma': 'no-cache',
                'referer': _0x15ca68(_0xdc848._0x16f93c),
                'sec-ch-ua': '\x22Not_A\x20Brand\x22;v=\x2299\x22,\x20\x22Google\x20Chrome\x22;v=\x22109\x22,\x20\x22Chromium\x22;v=\x22109\x22',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': _0x15ca68(_0xdc848._0x58c8a8),
                'sec-fetch-dest': _0x15ca68(_0xdc848._0x449635),
                'sec-fetch-mode': _0x15ca68(_0xdc848._0x2fa582),
                'sec-fetch-site': 'same-site',
                'user-agent': 'Mozilla/5.0\x20(Macintosh;\x20Intel\x20Mac\x20OS\x20X\x2010_15_7)\x20AppleWebKit/537.36\x20(KHTML,\x20like\x20Gecko)\x20Chrome/109.0.0.0\x20Safari/537.36'
            }
        });
        const _0x1499a9 = await _0x23768c[_0x15ca68(_0xdc848._0x2e8261)]();
        console['log'](_0x1499a9);
    } catch (_0x307ab8) {
        console[_0x15ca68(_0xdc848._0x56169a)](_0x307ab8);
    }
})());
```

Let us copy-paste this code into [AST Explorer](https://astexplorer.net) and
broadly review what we got here.

At topmost level of the program, there are three major parts (two 
`FunctionDeclaration` objects and one `ExpressionStatement`):

1. A small function that returns a hardcoded array with encoded string literals.
2. A bigger function that seems to do string decoding given an index(?) within
string array.
3. An IIFE that relies on the above two functions to get some of the string
values, but is otherwise quite similar to the code we started with.

[Screenshot 2](/2023-02-11_14.51.25.png)
[Screenshot 3](/2023-02-11_14.51.15.png)
[Screenshot 3](/2023-02-11_14.51.37.png)

What is going in this middle function? A quick Google search of the large
constant suggests that it has something to do with Base64 encoding, which 
is consistent with obfuscation settings we used. 

[Screenshot 4](/2023-02-11_14.58.55.png)

However it also seems to something beyond just Base64 as the strings in the
encoded array do not yield anything readable when decoded with Base64 algorithm.

[Screenshot 5](/2023-02-11_14.58.35.png)

At this point we don't quite know what it does exactly, but let us put that
question aside.

Our endgame is to replace the calls to decoder function (`_0x4ad0()` a.k.a.
`_0x15ca68()`) with the decoded string value that it would return. But since
we're just learning, let us start small by making the code slightly more 
readable. In the IIFE there's this pesky `_0xdc848` object that contains 
key-value pairs, with values being used as arguments for decoding function.
When the code below calls the decoding function, it indirectly gets the
argument from this object. Let us change the code so that values are used
directly and the `_0xdc848` object is gone. 

In the AST we got the following: there a `VariableDeclarator` with an 
`ObjectExpression` that has multiple `ObjectProperty` nodes in `properties`
array. Each `value` fields of these `ObjectProperty` objects points to 
a `NumericLiteral` node. So that's the `_0xdc848` object. Each reference
to this object (e.g. `_0xdc848._0x3da25d`) is a `MemberExpression` with 
object name at `object` field and key at `property` field (both represented
as `Identifier`s). 

[Screenshot 6](/2023-02-12_16.04.27.png)
[Screenshot 7](/2023-02-12_16.05.13.png)

So what we want to do is to replace `MemberExpression`s that reference the
constant map object with `NumericLiteral` nodes containing the final value,
then get rid of the `_0xdc848` as it won't be needed anymore. We do this
with the following transform:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "ast-transform", // not required
    visitor: {
      VariableDeclarator(path) {
        let node = path.node;
        if (!node.init) return;
        if (node.init.type != "ObjectExpression") return;
        let binding = path.scope.getBinding(node.id.name);
        if (!binding.constant) return;
        console.log(binding);
        let properties = node.init.properties;
        if (!properties) return;
        
        let kv = new Object();
        
        for (let prop of properties) {
          if (!t.isIdentifier(prop.key)) return;
          let key = prop.key.name;
          if (!t.isLiteral(prop.value)) return;
          let value = prop.value.value;
          kv[key] = value;
        }
        
        for (let refPath of binding.referencePaths) {
          if (!refPath.parentPath) return;
          let parentNode = refPath.parentPath.node;
          if (!t.isMemberExpression(parentNode)) return;
          let key = parentNode.property.name;
          let value = kv[key];
          refPath.parentPath.replaceWith(t.valueToNode(value));
        }
        
        path.remove();
      } 
    }
  };
}

```

We target `VariableDeclarator` nodes with a visitor function, do some quick
checks that variable declarator we have found is declaring a constant object.
Then we gather key-value pairs into a new object while checking that each value
is a literal (e.g. some numeric constant). Then we iterate across references
by using Babel scope and binding (see previous post on this) to replace
an object reference (`MemberExpression` node) with the final value (we get
it by saying `refPath.parentPath.node` as each entry in `Binding.referencePaths`
point to `Identifier` node that does the referencing). Finally, we remove the 
no longer needed object by removing the `VariableDeclarator` node from AST.

The IIFE at the bottom now looks like this:

```javascript
(async () => {
  const _0x15ca68 = _0x4ad0;

  try {
    const _0x23768c = await fetch('https://api.nike.com/cic/browse/v2?queryid=products&anonymousId=A7CA2A92E0F04E570767C7810552BBC5&country=au&endpoint=%2Fproduct_feed%2Frollup_threads%2Fv2%3Ffilter%3Dmarketplace(AU)%26filter%3Dlanguage(en-GB)%26filter%3DemployeePrice(true)%26filter%3DattributeIds(8529ff38-7de8-4f69-973c-9fdbfb102ed2%2C16633190-45e5-4830-a068-232ac7aea82c)%26anchor%3D24%26consumerChannelId%3Dd9a5bc42-4b9c-4976-858a-f159cf99c647%26count%3D24&language=en-GB&localizedRangeStr=%7BlowestPrice%7D%E2%80%94%7BhighestPrice%7D', {
      'headers': {
        'authority': _0x15ca68(0),
        'accept': _0x15ca68(1),
        'accept-language': _0x15ca68(2),
        'cache-control': 'no-cache',
        'origin': _0x15ca68(3),
        'pragma': 'no-cache',
        'referer': _0x15ca68(4),
        'sec-ch-ua': '\x22Not_A\x20Brand\x22;v=\x2299\x22,\x20\x22Google\x20Chrome\x22;v=\x22109\x22,\x20\x22Chromium\x22;v=\x22109\x22',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': _0x15ca68(5),
        'sec-fetch-dest': _0x15ca68(6),
        'sec-fetch-mode': _0x15ca68(7),
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0\x20(Macintosh;\x20Intel\x20Mac\x20OS\x20X\x2010_15_7)\x20AppleWebKit/537.36\x20(KHTML,\x20like\x20Gecko)\x20Chrome/109.0.0.0\x20Safari/537.36'
      }
    });

    const _0x1499a9 = await _0x23768c[_0x15ca68(8)]();

    console['log'](_0x1499a9);
  } catch (_0x307ab8) {
    console[_0x15ca68(9)](_0x307ab8);
  }
})();
```

[Screenshot 8](/2023-02-11_15.38.49.png)

Well, that's a bit better, but we still got some indirection in the code. There
are some variables/constants that do nothing but just server as another name for
something else in the code. One culprit is `_0x15ca68` in the IIFE, but there's
some more in the functions further up. What we can do is get rid of these 
secondary variables and replace all references to them with references to the
original value/object/function it points to.

The AST transform to do this is as follow:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "ast-transform", // not required
    visitor: {
      VariableDeclarator(path) {
        let node = path.node;
        if (!node.init) return;
        if (!t.isIdentifier(node.init)) return;
        let scope = path.scope;
        let binding = scope.getBinding(node.id.name);
        
        for (let refPath of binding.referencePaths) {
          refPath.replaceWith(node.init);
        }
        path.remove();
      } 
    }
  };
}
```

To recognise a `VariableDeclarator` node that introduces a secondary identifier,
we merely have to check if there's a `Identifier` node at `init` property.
If that is the case, we replace all references to this node with `Identifier`
at `init` property, so that all the referencing code uses the name of primary
variable/constant/function. Then we remove the redundant variable declaration
from the code.

Now the code is further simplified and looks like this:

```javascript
function _0x5d79() {
  const _0x3d5a8f = ['yxbPlM5PA2uUy29T', 'kI8Q', 'zw4Tr0iSzw4Tvvm7Ct0WlJKSzw47Ct0WlJG', 'Ahr0Chm6lY93D3CUBMLRzs5JB20', 'Ahr0Chm6lY93D3CUBMLRzs5JB20V', 'iM1Hy09tiG', 'zw1WDhK', 'y29YCW', 'ANnVBG', 'Bg9N'];

  _0x5d79 = function () {
    return _0x3d5a8f;
  };

  return _0x5d79();
}

function _0x4ad0(_0x5d79db, _0x4ad0a1) {
  const _0x150e0f = _0x5d79();

  _0x4ad0 = function (_0x2ee979, _0x4a74f2) {
    _0x2ee979 = _0x2ee979 - 0x0;
    let _0x299466 = _0x150e0f[_0x2ee979];

    if (_0x4ad0['sjCySo'] === undefined) {
      var _0x1cb49b = function (_0x307ab8) {
        const _0x4d32cc = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/=';
        let _0x19f00a = '';
        let _0xf75b57 = '';

        for (let _0x1806d0 = 0x0, _0x425bd6, _0x1bc5e5, _0x152116 = 0x0; _0x1bc5e5 = _0x307ab8['charAt'](_0x152116++); ~_0x1bc5e5 && (_0x425bd6 = _0x1806d0 % 0x4 ? _0x425bd6 * 0x40 + _0x1bc5e5 : _0x1bc5e5, _0x1806d0++ % 0x4) ? _0x19f00a += String['fromCharCode'](0xff & _0x425bd6 >> (-0x2 * _0x1806d0 & 0x6)) : 0x0) {
          _0x1bc5e5 = _0x4d32cc['indexOf'](_0x1bc5e5);
        }

        for (let _0x4858d8 = 0x0, _0x24c07d = _0x19f00a['length']; _0x4858d8 < _0x24c07d; _0x4858d8++) {
          _0xf75b57 += '%' + ('00' + _0x19f00a['charCodeAt'](_0x4858d8)['toString'](0x10))['slice'](-0x2);
        }

        return decodeURIComponent(_0xf75b57);
      };

      _0x4ad0['rQzPwo'] = _0x1cb49b;
      _0x5d79db = arguments;
      _0x4ad0['sjCySo'] = !![];
    }

    const _0x29a87a = _0x150e0f[0x0];

    const _0x23768c = _0x2ee979 + _0x29a87a;

    const _0x1499a9 = _0x5d79db[_0x23768c];

    if (!_0x1499a9) {
      _0x299466 = _0x4ad0['rQzPwo'](_0x299466);
      _0x5d79db[_0x23768c] = _0x299466;
    } else {
      _0x299466 = _0x1499a9;
    }

    return _0x299466;
  };

  return _0x4ad0(_0x5d79db, _0x4ad0a1);
}

(async () => {
  try {
    const _0x23768c = await fetch('https://api.nike.com/cic/browse/v2?queryid=products&anonymousId=A7CA2A92E0F04E570767C7810552BBC5&country=au&endpoint=%2Fproduct_feed%2Frollup_threads%2Fv2%3Ffilter%3Dmarketplace(AU)%26filter%3Dlanguage(en-GB)%26filter%3DemployeePrice(true)%26filter%3DattributeIds(8529ff38-7de8-4f69-973c-9fdbfb102ed2%2C16633190-45e5-4830-a068-232ac7aea82c)%26anchor%3D24%26consumerChannelId%3Dd9a5bc42-4b9c-4976-858a-f159cf99c647%26count%3D24&language=en-GB&localizedRangeStr=%7BlowestPrice%7D%E2%80%94%7BhighestPrice%7D', {
      'headers': {
        'authority': _0x4ad0(0),
        'accept': _0x4ad0(1),
        'accept-language': _0x4ad0(2),
        'cache-control': 'no-cache',
        'origin': _0x4ad0(3),
        'pragma': 'no-cache',
        'referer': _0x4ad0(4),
        'sec-ch-ua': '\x22Not_A\x20Brand\x22;v=\x2299\x22,\x20\x22Google\x20Chrome\x22;v=\x22109\x22,\x20\x22Chromium\x22;v=\x22109\x22',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': _0x4ad0(5),
        'sec-fetch-dest': _0x4ad0(6),
        'sec-fetch-mode': _0x4ad0(7),
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0\x20(Macintosh;\x20Intel\x20Mac\x20OS\x20X\x2010_15_7)\x20AppleWebKit/537.36\x20(KHTML,\x20like\x20Gecko)\x20Chrome/109.0.0.0\x20Safari/537.36'
      }
    });

    const _0x1499a9 = await _0x23768c[_0x4ad0(8)]();

    console['log'](_0x1499a9);
  } catch (_0x307ab8) {
    console[_0x4ad0(9)](_0x307ab8);
  }
})();
```

[Screenshot 9](/2023-02-11_16.18.05.png)

In the IIFE we got direct calls to decoder function, as well as slightly
simplified code in the decoder function itself. We're getting close now.
Let us rename some of the identifiers to more readable form by applying 
another simple transformation:

```javascript
const betterNames = {
  "_0x4ad0": "decode",
  "_0x3d5a8f": "encodedStrings",
  "_0x5d79": "getEncodedStrings",
  "_0x4d32cc": "base64Alphabet",
  "_0x23768c": "response",
  "_0x1499a9": "json"
};

export default function (babel) {
  const { types: t } = babel;

  return {
    name: "ast-transform", // not required
    visitor: {
      Identifier(path) {
        let name = path.node.name;
        if (name in betterNames) {
          let newName = betterNames[name];
          let newIdentifier = t.identifier(newName);
          
          let scope = path.scope;
          let binding = scope.getBinding(name);
          
          for (let refPath of binding.referencePaths) {
            refPath.replaceWith(newIdentifier);
          }
          
          path.replaceWith(newIdentifier);
        }
      }
    }
  };
}
```

The code now looks like this:

```javascript
function getEncodedStrings() {
  const encodedStrings = ['yxbPlM5PA2uUy29T', 'kI8Q', 'zw4Tr0iSzw4Tvvm7Ct0WlJKSzw47Ct0WlJG', 'Ahr0Chm6lY93D3CUBMLRzs5JB20', 'Ahr0Chm6lY93D3CUBMLRzs5JB20V', 'iM1Hy09tiG', 'zw1WDhK', 'y29YCW', 'ANnVBG', 'Bg9N'];

  getEncodedStrings = function () {
    return encodedStrings;
  };

  return getEncodedStrings();
}

function decode(_0x5d79db, _0x4ad0a1) {
  const _0x150e0f = getEncodedStrings();

  decode = function (_0x2ee979, _0x4a74f2) {
    _0x2ee979 = _0x2ee979 - 0x0;
    let _0x299466 = _0x150e0f[_0x2ee979];

    if (decode['sjCySo'] === undefined) {
      var _0x1cb49b = function (_0x307ab8) {
        const base64Alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/=';
        let _0x19f00a = '';
        let _0xf75b57 = '';

        for (let _0x1806d0 = 0x0, _0x425bd6, _0x1bc5e5, _0x152116 = 0x0; _0x1bc5e5 = _0x307ab8['charAt'](_0x152116++); ~_0x1bc5e5 && (_0x425bd6 = _0x1806d0 % 0x4 ? _0x425bd6 * 0x40 + _0x1bc5e5 : _0x1bc5e5, _0x1806d0++ % 0x4) ? _0x19f00a += String['fromCharCode'](0xff & _0x425bd6 >> (-0x2 * _0x1806d0 & 0x6)) : 0x0) {
          _0x1bc5e5 = base64Alphabet['indexOf'](_0x1bc5e5);
        }

        for (let _0x4858d8 = 0x0, _0x24c07d = _0x19f00a['length']; _0x4858d8 < _0x24c07d; _0x4858d8++) {
          _0xf75b57 += '%' + ('00' + _0x19f00a['charCodeAt'](_0x4858d8)['toString'](0x10))['slice'](-0x2);
        }

        return decodeURIComponent(_0xf75b57);
      };

      decode['rQzPwo'] = _0x1cb49b;
      _0x5d79db = arguments;
      decode['sjCySo'] = !![];
    }

    const _0x29a87a = _0x150e0f[0x0];
    const response = _0x2ee979 + _0x29a87a;
    const json = _0x5d79db[response];

    if (!json) {
      _0x299466 = decode['rQzPwo'](_0x299466);
      _0x5d79db[response] = _0x299466;
    } else {
      _0x299466 = json;
    }

    return _0x299466;
  };

  return decode(_0x5d79db, _0x4ad0a1);
}

(async () => {
  try {
    const response = await fetch('https://api.nike.com/cic/browse/v2?queryid=products&anonymousId=A7CA2A92E0F04E570767C7810552BBC5&country=au&endpoint=%2Fproduct_feed%2Frollup_threads%2Fv2%3Ffilter%3Dmarketplace(AU)%26filter%3Dlanguage(en-GB)%26filter%3DemployeePrice(true)%26filter%3DattributeIds(8529ff38-7de8-4f69-973c-9fdbfb102ed2%2C16633190-45e5-4830-a068-232ac7aea82c)%26anchor%3D24%26consumerChannelId%3Dd9a5bc42-4b9c-4976-858a-f159cf99c647%26count%3D24&language=en-GB&localizedRangeStr=%7BlowestPrice%7D%E2%80%94%7BhighestPrice%7D', {
      'headers': {
        'authority': decode(0),
        'accept': decode(1),
        'accept-language': decode(2),
        'cache-control': 'no-cache',
        'origin': decode(3),
        'pragma': 'no-cache',
        'referer': decode(4),
        'sec-ch-ua': '\x22Not_A\x20Brand\x22;v=\x2299\x22,\x20\x22Google\x20Chrome\x22;v=\x22109\x22,\x20\x22Chromium\x22;v=\x22109\x22',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': decode(5),
        'sec-fetch-dest': decode(6),
        'sec-fetch-mode': decode(7),
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0\x20(Macintosh;\x20Intel\x20Mac\x20OS\x20X\x2010_15_7)\x20AppleWebKit/537.36\x20(KHTML,\x20like\x20Gecko)\x20Chrome/109.0.0.0\x20Safari/537.36'
      }
    });
    const json = await response[decode(8)]();
    console['log'](json);
  } catch (_0x307ab8) {
    console[decode(9)](_0x307ab8);
  }
})();
```

[Screenshot 10](/2023-02-11_16.35.02.png)

One minor issue is that it incorrectly renamed something to `response` and
`json` in the `decode()` function, but we can afford not to worry about this,
as this functions is going away soon.

We are getting close to our grand finale, but there's one small thing we would
like to fix. In the `decode()` function there is a single call to 
`getEncodedStrings()` that returns a hardcoded array of concealed strings.
The `getEncodedStrings()` function is not called anywhere else, so we
can do one more quick transform to replace a call to this function 
(`CallExpression` object) with the array itself (`ArrayExpression` object). We
write another quick transform to do so and also remove the `getEncodedStrings()`
function:

```javascript
export default function (babel) {
  const { types: t } = babel;

  return {
    name: "ast-transform", // not required
    visitor: {
      FunctionDeclaration(path) {
        let node = path.node;
        if (node.id.name === "getEncodedStrings") {
          let encodedStringArrayExpr = node.body.body[0].declarations[0].init;
          let scope = path.scope;
          let binding = scope.getBinding(node.id.name);
          
          for (let refPath of binding.referencePaths) {
            if (refPath.parentPath.node.type === "CallExpression") {
              refPath.parentPath.replaceWith(encodedStringArrayExpr);
            }
          }
          
          path.remove();
        }
      }        
    }
  };
}

```

The function that returns an array is gone and array is now hardcoded into
`decode()` function:

```javascript
function decode(_0x5d79db, _0x4ad0a1) {
  const _0x150e0f = ['yxbPlM5PA2uUy29T', 'kI8Q', 'zw4Tr0iSzw4Tvvm7Ct0WlJKSzw47Ct0WlJG', 'Ahr0Chm6lY93D3CUBMLRzs5JB20', 'Ahr0Chm6lY93D3CUBMLRzs5JB20V', 'iM1Hy09tiG', 'zw1WDhK', 'y29YCW', 'ANnVBG', 'Bg9N'];


```

[Screenshot 11](/2023-02-11_17.02.49.png)

What we have achieved is the following:

* String decoding logic is now contained into a single function - `decode()`.
The code of this function could be regenerated with Babel and passed into 
`eval()`, `Function.call()` or Node's [`vm` API](https://nodejs.org/api/vm.html)
to get decoded values.
* We have explicit argument values to use with `decode()` in the IIFE.

These two this are enough to undo the string concealing. For the sake of
simplicity we will refrain from regenerating code for `decode()` function 
and will copy-paste it into AST Explorers transform pane instead. The 
final transform is as follows:

```javascript
function decode(_0x5d79db, _0x4ad0a1) {
  ...
}

export default function (babel) {
  const { types: t } = babel;

  return {
    name: "ast-transform", // not required
    visitor: {
      CallExpression(path) {
        let node = path.node;
        if (node.callee.name != "decode") return;
        if (!node.arguments) return;
        console.log(node);
        if (node.arguments.length != 1) return;
        let arg = node.arguments[0].value;
        let decodedStr = decode(arg);
        console.log(decodedStr);
        path.replaceWith(t.valueToNode(decodedStr));
      },
      FunctionDeclaration(path) {
        if (path.node.id.name === "decode") path.remove();
      }
    }
  };
}
```

This yields a deobfuscated version of code that is quite similar to what 
we had in the initial snippet:

```javascript
(async () => {
  try {
    const response = await fetch('https://api.nike.com/cic/browse/v2?queryid=products&anonymousId=A7CA2A92E0F04E570767C7810552BBC5&country=au&endpoint=%2Fproduct_feed%2Frollup_threads%2Fv2%3Ffilter%3Dmarketplace(AU)%26filter%3Dlanguage(en-GB)%26filter%3DemployeePrice(true)%26filter%3DattributeIds(8529ff38-7de8-4f69-973c-9fdbfb102ed2%2C16633190-45e5-4830-a068-232ac7aea82c)%26anchor%3D24%26consumerChannelId%3Dd9a5bc42-4b9c-4976-858a-f159cf99c647%26count%3D24&language=en-GB&localizedRangeStr=%7BlowestPrice%7D%E2%80%94%7BhighestPrice%7D', {
      'headers': {
        'authority': "api.nike.com",
        'accept': "*/*",
        'accept-language': "en-GB,en-US;q=0.9,en;q=0.8",
        'cache-control': 'no-cache',
        'origin': "https://www.nike.com",
        'pragma': 'no-cache',
        'referer': "https://www.nike.com/",
        'sec-ch-ua': '\x22Not_A\x20Brand\x22;v=\x2299\x22,\x20\x22Google\x20Chrome\x22;v=\x22109\x22,\x20\x22Chromium\x22;v=\x22109\x22',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': "\"macOS\"",
        'sec-fetch-dest': "empty",
        'sec-fetch-mode': "cors",
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0\x20(Macintosh;\x20Intel\x20Mac\x20OS\x20X\x2010_15_7)\x20AppleWebKit/537.36\x20(KHTML,\x20like\x20Gecko)\x20Chrome/109.0.0.0\x20Safari/537.36'
      }
    });
    const json = await response["json"]();
    console['log'](json);
  } catch (_0x307ab8) {
    console["log"](_0x307ab8);
  }
})();

```

[Screenshot 12](/2023-02-11_17.35.49.png)
