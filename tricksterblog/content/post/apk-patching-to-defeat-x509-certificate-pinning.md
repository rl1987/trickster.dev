+++
author = "rl1987"
title = "APK patching to defeat X.509 certificate pinning"
date = "2026-01-31"
draft = true
tags = ["scraping", "osint", "security"]
+++

X.509 cert pinning is a security mechanism again man-in-the-middle attacks
commonly used in mobile applications to prevent API traffic interception. It
often gets in the way when we want to explore communications between mobile
app and backend systems. Previously I have shown how to use Frida to defeat it
at runtime. However, another approach is possible. We can patch application
to remove or bypass certificate pinning code, thus avoiding the need to use 
Frida. There will be the following steps involved in this approach:

1. Unpacking the APK with apktool.
2.  Patching smali code and (if needed) tweaking network security policy.
3. Recompiling the APK.
4. Signing the APK.
5. Installing the APK into device or emulator configured to use MITM server as
proxy.


WRITEME
