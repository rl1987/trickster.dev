+++
author = "rl1987"
draft = true
title = "Scraping Next.js web sites in 2025"
date = "2025-10-31"
tags = ["scraping"]
+++

When looking into some targets for web scraping, you may come across pages
that contain a lot of data represented in JSONesque (but not quite JSON) format
passed to `self.__next_f.push()` Javascript function calls. What's going on 
here and how do we parse this stuff? To understand what this is about, we must
go through a little journey across the technological landscape of the modern
web.

So, it's widely known that [React](https://react.dev/) is a very prominent 
frontend framework to develop web apps in JavaScript. Altough one can develop
web apps with the very basics - HTML, CSS and vanilla JavaScript, doing so is
too simple for enterprise software teams and tech startups drunk on that sweet
VC funding. They need more powerful abstractions, such as reusable components,
UI state management, Virtual DOM to optimize performance by only redrawing
parts of UI that changed and JSX syntax that extends Javascript language into
Javascript-HTML hybrid dialect. More generally, React has emerged as a winner
among many ZIRP-era Javascript frameworks by addressing the reactivity problem 
in web app development: how do we associate internal app state with visible UI
stuff and how do we keep them in sync when one or the other changes.

Primarily React is only a frontend framework meant to develop code that runs in
a browser. React alone cannot be used for full stack web development, as we
also need something for the backend side of the app. To fill this gap, Next.js
was developed. Next.js is another Javascript framework that works with React
to provide features like request routing, performance optimization (e.g. 
making images smaller depending on the needs of frontend side) and Server Side
Rendering (SSR). The latter will become important for our purposes in a moment.
In addition to all of that, Next.js provides some tooling for easier deployment 
and nicer developer experience.

* `__NEXT_DATA__`
* `self.__next_f.push` / Next.js flight data
* njsparser

