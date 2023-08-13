+++
author = "rl1987"
title = "Solving a simple JS challenge with sandboxing"
date = "2023-08-20"
draft = true
tags = ["scraping", "reverse-engineering", "python", "javascript"]
+++


WRITEME


```javascript
export default function (babel) {
  const { types: t } = babel;
  
  return {
    name: "ast-transform", // not required
    visitor: {
      "Program|IfStatement|Expression|ExpressionStatement"(path) {
        t.removeComments(path.node);
      }
    }
  };
}
```
