+++
author = "rl1987"
title = "ImageMagick: programmable image processing toolkit"
date = "2022-08-14"
draft = true
tags = ["automation"]
+++

[ImageMagick](https://imagemagick.org) is a set of CLI tools and C library for performing a variety of digital image handling tasks, 
such as converting between formats, resizing, mirroring, rotating, adjusting colors, rendering
text, drawing shapes and so on. In many cases ImageMagick is not being used directly, but exists as
part of the hidden substrate of C code that the modern shiny stuff is built upon. For example, it may
be used to generate thumbnails of images that users uploaded to a web application. ImageMagick supports
more than 200 image formats and run on all the major operating systems. If you're running Linux, macOS
or other well established Unix system it will most likely be available through your package manager.

ImageMagick can be used through the following CLI tools:

* `animate` - animate a sequence of images (requires X Windows).
* `conjure` - run an image processing script written in XML-based Magick Scripting Language (MSL).
* `display` - show a single image (requires X Windows).
* `magick` - general purpose CLI tool for pretty much everything. This one is recommended for modern usage. 
Others are leftovers from legacy versions of ImageMagick.
* `convert` - convert between image formats, optionally with some tranformations.
* `composite` - overlap or overlay two or more image on each other.
* `montage` - combine several images into a single output image.
* `compare` - show difference between images.
* `identify` - describes one or more image files and prints their metadata.
* `import` - save a screenshot of entire X Windows screen or some portion of it.
* `stream` - extract raw values of pixel components.

WRITEME: extracting image metadata

WRITEME: basic stuff: converting do different format, converting to grayscale, resizing, making thumbnails

WRITEME: convolution, etc.

WRITEME: library and bindings

WRITEME: an example to clean up simple captcha image

