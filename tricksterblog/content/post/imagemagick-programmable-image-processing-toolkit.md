+++
author = "rl1987"
title = "ImageMagick: programmable image processing toolkit"
date = "2022-08-14"
draft = true
tags = ["automation"]
+++

[ImageMagick](https://imagemagick.org) is a set of CLI tools and a C library for performing a variety of digital image handling tasks, 
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

Let us start simple by extracting some metadata from image files. For the sake of example,
we will use a geotagged image file that contains GPS coordinates within EXIF fields.

```
$ wget https://www.geoimgr.com/images/samples/irland-dingle.jpg
--2022-08-13 13:10:14--  https://www.geoimgr.com/images/samples/irland-dingle.jpg
Resolving www.geoimgr.com (www.geoimgr.com)... 108.157.214.28, 108.157.214.104, 108.157.214.75, ...
Connecting to www.geoimgr.com (www.geoimgr.com)|108.157.214.28|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 694078 (678K) [image/jpeg]
Saving to: ‘irland-dingle.jpg’

irland-dingle.jpg                                  100%[================================================================================================================>] 677,81K   979KB/s    in 0,7s    

2022-08-13 13:10:16 (979 KB/s) - ‘irland-dingle.jpg’ saved [694078/694078]

$ file irland-dingle.jpg 
irland-dingle.jpg: JPEG image data, JFIF standard 1.01, aspect ratio, density 1x1, segment length 16, Exif Standard: [TIFF image data, little-endian, direntries=14, manufacturer=Panasonic, model=DMC-FX60, orientation=upper-left, xresolution=202, yresolution=210, resolutionunit=2, software=Ver.1.0  , datetime=2012:09:16 16:58:02, GPS-DataTIFF image data, little-endian, direntries=14, manufacturer=Panasonic, model=DMC-FX60, orientation=upper-left, xresolution=202, yresolution=210, resolutionunit=2, software=Ver.1.0  , datetime=2012:09:16 16:58:02, GPS-Data], baseline, precision 8, 2048x1536, components 3
$ magick identify -verbose irland-dingle.jpg 
Image:
  Filename: irland-dingle.jpg
  Format: JPEG (Joint Photographic Experts Group JFIF format)
  Mime type: image/jpeg
  Class: DirectClass
  Geometry: 2048x1536+0+0
  Resolution: 92.16x92.16
  Print size: 22.2222x16.6667
  Units: PixelsPerInch
  Colorspace: sRGB
  Type: TrueColor
  Base type: Undefined
  Endianness: Undefined
  Depth: 8-bit
  Channel depth:
    Red: 8-bit
    Green: 8-bit
    Blue: 8-bit
  Channel statistics:
    Pixels: 3145728
    Red:
      min: 0  (0)
      max: 255 (1)
      mean: 147.255 (0.57747)
      median: 139 (0.545098)
      standard deviation: 71.5477 (0.280579)
      kurtosis: -1.25311
      skewness: 0.0244421
      entropy: 0.960027
    Green:
      min: 0  (0)
      max: 255 (1)
      mean: 146.551 (0.574708)
      median: 137 (0.537255)
      standard deviation: 73.5709 (0.288513)
      kurtosis: -1.26019
      skewness: 0.0407684
      entropy: 0.957017
    Blue:
      min: 0  (0)
      max: 255 (1)
      mean: 148.024 (0.580487)
      median: 140 (0.54902)
      standard deviation: 73.7421 (0.289185)
      kurtosis: -1.28316
      skewness: 0.0582366
      entropy: 0.937305
  Image statistics:
    Overall:
      min: 0  (0)
      max: 255 (1)
      mean: 147.277 (0.577555)
      median: 138.667 (0.543791)
      standard deviation: 72.9536 (0.286092)
      kurtosis: -1.26427
      skewness: 0.0417203
      entropy: 0.951449
  Rendering intent: Perceptual
  Gamma: 0.454545
  Chromaticity:
    red primary: (0.64,0.33)
    green primary: (0.3,0.6)
    blue primary: (0.15,0.06)
    white point: (0.3127,0.329)
  Matte color: grey74
  Background color: white
  Border color: srgb(223,223,223)
  Transparent color: none
  Interlace: None
  Intensity: Undefined
  Compose: Over
  Page geometry: 2048x1536+0+0
  Dispose: Undefined
  Iterations: 0
  Compression: JPEG
  Quality: 90
  Orientation: TopLeft
  Profiles:
    Profile-exif: 16766 bytes
  Properties:
    date:create: 2022-08-13T10:10:16+00:00
    date:modify: 2019-07-13T17:45:39+00:00
    date:timestamp: 2022-08-13T10:13:31+00:00
    exif:ColorSpace: 1
    exif:ComponentsConfiguration: ....
    exif:CompressedBitsPerPixel: 4/1
    exif:Contrast: 0
    exif:CustomRendered: 0
    exif:DateTime: 2012:09:16 16:58:02
    exif:DateTimeDigitized: 2012:09:16 16:58:02
    exif:DateTimeOriginal: 2012:09:16 16:58:02
    exif:DigitalZoomRatio: 0/10
    exif:ExifOffset: 648
    exif:ExifVersion: 0221
    exif:ExposureBiasValue: 0/100
    exif:ExposureMode: 0
    exif:ExposureProgram: 2
    exif:ExposureTime: 10/2000
    exif:FileSource: .
    exif:Flash: 24
    exif:FlashPixVersion: 0100
    exif:FNumber: 40/10
    exif:FocalLength: 77/10
    exif:FocalLengthIn35mmFilm: 43
    exif:GainControl: 0
    exif:GPSInfo: 10396
    exif:GPSLatitude: 52/1, 8/1, 20155/942
    exif:GPSLatitudeRef: N
    exif:GPSLongitude: 10/1, 16/1, 17981/630
    exif:GPSLongitudeRef: W
    exif:GPSVersionID: ....
    exif:InteroperabilityOffset: 10366
    exif:LightSource: 0
    exif:Make: Panasonic
    exif:MakerNote: Panasonic...=......................................................... ...................................%... ...........!.... ..h..."...........#...........$...........%.......p'..&.......0291'...........(...........).......?...*...........+...........,...........-......................./...........0...........1...........2...........3........'..4...........5...........6.......??..7...........8...........:...........;...........<.......??..=...........>...........?...........M........'..N...*...?'..O...........W...........Y...........]...........^...........a.......?'..b...........c...................0132........%...................................?.......................................................................b(..............DV..EP..??DB?.??AF?.??..??..??.0??..ʯ2.??..??..??..??????..??..??..??X.???.ȯ@.د????..??..Ư..ίB.ү..Я(.??v.??>.??>.ԯ0.?? .?(.?..?..௯.??.??.??.?..??..گ..֯..?........?..?...?...?...?..??ST.. ?.."?..$?..&?..(?..*?..,?...?..0?..2?..4?..6?..8?..:?..<?..`?..b?..d?..h?..f?..j?..x?..|?..~?..>?..p?..r?..t?..v?..R?..L?..N?..P?..??AEn..?,..?X..?,..?...?...?..*?..,?..$??.>?..2? ..??.(?...?.. ?f."??.0?#.&?..??..????4?...???.???.?..??..?????..?...???¦??.?...?..??...?...???.?...???.?..T?..V?..D??.J??.F??.H?..N?..^?..R?..X?..@?..B??.`?..Z?..\?...??.d?...?..b?...?..L?..??..??..??..6?..j?..l?..n?6.Ħ..Ʀ..Ȧ].ʦ9.̦..Φa.Ц..֦..ئ..Ҧ..Ԧ..??#.??..??#.??..0?x..?x..?P..?W..?#..?...?...?@.2?..??WB2..??..?...?...?...?..h?..`?o.d??.f?..@??.B?..D?..F? .??j.???.??..??..??u.??".??s.??..???.??..??..???.??j.???.??..??..j?..l?!..??..?..b??.??d.Ȩ..¨?.ʨ?.Ĩ??̨..ƨ..Ψ..Ш..$?..&?.. ?.."?..(??.*?..,?...?..0?..2?..H??.J?..L??.N?..P??.R?..T??.V?...?\..?j..?...?...?...?...?...?...?...?...?...?...?...?..??YC?.N?..P?..R?..T?..D?..F???H?..J?..L?..8?..:?..<?..>?...?..0??.2?fD4?".6?...............?`.`?..b?..d?Xrf?Xrh?]]j?..l?..n?...?...?...?...?...?...?...?...?...?...?..???.??..???.??..??..X?..Z?..\?..^? ..?...?..????ª??Ī??ƪ??Ȫ????CM..?. p.?..??..ک..ܩ..??DS:..?...?...??..??..?...?...??U.?uU.?"".?! .?"".?! .?..??ISn..?..??..??..???.??...?...?e..?...?e..?...?...??..?<..?n..?N..?...??..??..??..??..??..??..??..??..??..??.??FD?.`?..b?...?...?...?...?...?...?...?...?...?...?...?...?...?...?...?...?..@?..B?..D?..F?..H?..J?..L?..N?..P?..R?..T?..V?..X?..Z?..\?..^?..ħ..̧..Χ..Ч..ʧd.§..??ATB.<?.."?..$?..&?..(?..*?..,?...?..0?..2?..4?..6?..8?..:?..>?..??IAn.???.???.??..??..??????????????????..??..??..??..????????????????.?r..?...?...?...?...?...?!..?...?...?..........................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................MOIS..?...,...?...8.,.p.L.x.?.....?... .?... .?...?.?.`.?.?.....@.(.T.,.?.<.?.(...h.?...p...h.D.....?.$...d.8.?.x. ...?.T.?.?.........?.....L...X.?.?. ...?.?.?...H.x.8...?.@.t.H...?.@.?.4.?.(...?...........?.....?.@.`...?...D.D...?...$.?.d.<.x.?.?.?.?.?...?.?.....?.....?.?.?.?.?.?.?.?.?.?.?.?.?.?.?.?.?.?.?.?.J.J.....}.?.......?.?. . .?.?.....?.?.....?.?.t.t.H.H.0.8.?.`.......D.H.?.?.l.?...?.d.$.?.?.`.x...t...?.?...?.?...?.$.?.?.$.?.....?.....8.,...|.?.?.?.?.....?.8...D.?...?...?.l...H.....?.@.....?.4.d.0.D.?.?.d.T...d...`...?...x.X. .<.0.?.4.?...$.?.?.?...?.<.?...?.P...?.?.|.$...?.x.@.$.?.?...?.?.2.2.9.2.9.9.......?.?.?.?.......?.?.?.?.............?.?.?.?.m.m.m.m.m.....?.k.k.?.?.?...Z.H.H.i.i.P.P.I.I.%.%.........;.AEBM?.....2.?.?.....?.2.V.?...5.?.?.s.[.?.9.j.f.?...y.?.X.a...-.f.?.?.?.?.?.t.?.?.).5.=...?.?.?.].H.?.?.`.?.....?...a.g.....?.-.....1.S.?.?...?.?.?.?.B.e.?.?.?.?.N.C...!.@.?.?.s.G.O...X.?.?.?.f.I.?.1.?.k.?...,.?.?. .?.E.?.?.....?.?.......k.?.V...?.?.?.`.?.?.u.?.?.P...?.?.?.?...i...?.l.+.k...PRST................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................FCCV....?...?.?.?.?.?.......?.?.r.?.X.......................X.....*...".?...../.?.....?.9.K...X.?.?...|.?.?.....?.#...u.?.?...?.?.......?.?.....?.|.?.*.A.`...{.?.......?.5.m.?.T.S.....%...?...?.......?.?.....?.y.?.U.]...?.?.?.&.-.?.?.?.?.I.?.......r.g.h.......?.#.?.?.....?.|.,.....?.?.?. .T.R.?...:.?.?.....2...?.?.............?.......?.v...?.?.#.H.4.p.....D.A...o...J...?.H.`.i.?... .....(...?.....?.....q.R...?.?.?.?.?.?...?.8.H...%.....?...x.E.7.D.%.D...0...;.....?.7.?.-...]..._...h.?.F.?...?.?.F.?.a.?.(.?.?.?.{.?...w.V.?...?.?.?.?...m.*.h.?.l.$.i.?...?.....?.s.?.j.?.m.?.....X.g.t.'...e...?.?.?.?.U...I...\.?.?.S.?.A...?.+.?.?.....L.?.?.?.?...?...?.m.R.?.u.u.?.?.?.....?.?.e.?.5...\.@.l.c.......7.?.?.?.{.?.l.?.?...X.?.p...?.?.?.P.?...?.i.?.9...G./.l.b...,.....=...>.r.F.?.?...Z.r.?.?.?.?.#.&...g.P...?.i.?.\...?.:...?.?...?...?.q.......;.?...?.?.?.?.?...P.?.?._.4.Z.?.|.?.?.;.?.?.?.e.................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................WBCZ................................................................................................................................................BMHL........+.......................................................................................................................................F060909280144.b,9999:99:99 00:00:00...........................................................................................9999:99:99 00:00:00.............................9999:99:99 00:00:00.............................9999:99:99 00:00:00.9999:99:99 00:00:00.
    exif:MaxApertureValue: 30/10
    exif:MeteringMode: 5
    exif:Model: DMC-FX60
    exif:PhotographicSensitivity: 80
    exif:PixelXDimension: 2048
    exif:PixelYDimension: 1536
    exif:PrintImageMatching: PrintIM.0250..................d.............................?.................?..........................'.......'.......'..?....'.......'..^....'.......'..?....'..?....'......................................
    exif:Saturation: 0
    exif:SceneCaptureType: 0
    exif:SceneType: .
    exif:SensingMethod: 2
    exif:Sharpness: 0
    exif:Software: Ver.1.0  
    exif:thumbnail:Compression: 6
    exif:thumbnail:InteroperabilityIndex: R98
    exif:thumbnail:InteroperabilityVersion: 0100
    exif:thumbnail:JPEGInterchangeFormat: 10628
    exif:thumbnail:JPEGInterchangeFormatLength: 6131
    exif:thumbnail:Orientation: 1
    exif:thumbnail:ResolutionUnit: 2
    exif:thumbnail:XResolution: 180/1
    exif:thumbnail:YCbCrPositioning: 2
    exif:thumbnail:YResolution: 180/1
    exif:WhiteBalance: 0
    exif:YCbCrPositioning: 2
    jpeg:colorspace: 2
    jpeg:sampling-factor: 2x2,1x1,1x1
    signature: 43f09d8ff5c5df045697fccde02cd88200c8c657eb4c2458a48c72a4cd8a9576
    unknown: ................................................................
  Artifacts:
    verbose: true
  Tainted: False
  Filesize: 694078B
  Number pixels: 3.14573M
  Pixel cache type: Memory
  Pixels per second: 74.1853MP
  User time: 0.030u
  Elapsed time: 0:01.042
  Version: ImageMagick 7.1.0-45 Q16-HDRI aarch64 20319 https://imagemagick.org
```

We see that ImageMagick was able to print far more information on the image file than a standard Unix
file(1) utility. Not only it printed some image representation characteristics, but it also gave us
the entire EXIF metadata including coordinates, camera settings and information on technical properties
of the camera. All of this leaks quite a bit of information on how, where and when the picture was 
taken and can be valuable to those working on digital forensics. Furthemore, it computed various 
statistical properties of pixel component value distribution within the image (e.g. mean, median, 
standard deviation, entropy). 

Let us try doing some transformations on the image. Converting the image file to another format is rather
simple:

```
$ magick convert irland-dingle.jpg irland-dingle.png 
$ magick identify irland-dingle.png 
irland-dingle.png PNG 2048x1536 2048x1536+0+0 8-bit sRGB 3.22077MiB 0.000u 0:00.000
```

What if we wanted to make it grayscale? The `convert` (sub-)command can also be used for this:

```
$ convert -colorspace Gray irland-dingle.png irland-dingle-gray.png
$ magick identify irland-dingle-gray.png                           
irland-dingle-gray.png PNG 2048x1536 2048x1536+0+0 8-bit Gray 256c 1.36152MiB 0.000u 0:00.001
```

That's one way to do this. For another ways, see:

* [Convert RGB to Grayscale in ImageMagick command-line](https://stackoverflow.com/questions/13317753/convert-rgb-to-grayscale-in-imagemagick-command-line) on StackOverflow

Resizing the image is also fairly simple:

```
$ magick convert irland-dingle.png -resize 64x64 irland-dingle-thumb.png
$ magick identify irland-dingle-thumb.png 
irland-dingle-thumb.png PNG 64x48 64x48+0+0 8-bit sRGB 28196B 0.000u 0:00.000
```

Note that by default this will keep the original aspect ratio of the image, thus the result image
may not be of size you passed into `-resize` argument or may have some empty parts. To force the
resizing into an exact size we provide, we need to use exclamation marks next to width and height values:

```
$ magick convert irland-dingle.png -resize 64\!x64\! irland-dingle-thumb-forced.png
```

[Screenshot 1](/2022-08-13_13.39.08.png)

For further information on resizing, see the [official documentation](https://legacy.imagemagick.org/Usage/resize/#resize).

However there is more to image processing than simple stuff like this. Digital image processing is a fairly
large field that deals with computational handling of image data for applications such as image compression,
computational photography, medical imaging, augmented reality, computer vision and others. 

One of the foundational techniques of digital image processing is convolutions that entails applying a
linear-algebra based filter on images. Convolution kernel is a two dimensional table of numbers (matrix)
that defines how the output image is created from input image. For example, low pass filter that implements
a simple image blurring can be implemented by a square matrix with each member being a constant:

```
$ magick convert irland-dingle.png -convolve "3x3: 0.1111, 0.1111, 0.1111  0.1111, 0.1111, 0.1111  0.1111, 0.1111, 0.1111" irland-dingle-blur.png
```

In fact, ImageMagick has some pre-made kernels for Gaussian blurring, among other applications:

```
$ magick convert irland-dingle.png -convolve Gaussian:0x8 irland-dingle-blur-gaussian.png
```

[Screenshot 2](/2022-08-13_14.05.19.png)

Since ImageMagick is a bunch of CLI tools it can already be used as part of automation scripts
by calling magick(1) program as subprocess or by writing a shell script that launches it with
the appropriate arguments. However, ImageMagick also exposes two kinds of C APIs. 
[MagickWand](https://imagemagick.org/script/magick-wand.php) is high-level, thread safe API
and [MagickCore](https://imagemagick.org/script/magick-core.php) is a low-level one. Most
developers should only consider using MagickWand. Don't worry if you don't want to deal with
C programming language. Wrappers in multiple popular programming languages are available:

* [Magick++](https://imagemagick.org/script/magick++.php) for C++.
* [Go Imagick](https://github.com/gographics/imagick) for Go.
* [JMagick](http://www.jmagick.org/) for Java.
* [Wand](https://docs.wand-py.org/en/0.6.9/) for Python.
* [MagickRust](https://github.com/nlfiedler/magick-rust) for Rust.

For a real-world code that uses ImageMagick, see [textcleaner](http://www.fmwconcepts.com/imagemagick/textcleaner/index.php)
script for cleaning up images of text before applying OCR on them. Potentially something like
this can be implemented to deal with simple image captchas that can be decoded with something
like Tesseract when proper pre-processing has been applied.
