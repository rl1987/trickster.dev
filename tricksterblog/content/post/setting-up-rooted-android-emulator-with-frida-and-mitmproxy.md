+++
author = "rl1987"
title = "Setting up rooted Android emulator with Frida and mitmproxy "
date = "2025-09-30"
draft = true
tags = ["security", "android", "mitmproxy"]
+++

Previously I have covered how to set up [mitmproxy](https://www.mitmproxy.org/) 
with [Android emulator](/post/setting-up-mitmproxy-with-android/) or iOS device
for the purposes of mobile app traffic interception. However, there is more to
mobile app hacking than that. Not all apps allow their API calls to be 
hijacked by the simple setup I have described earlier. Some of the more secure
apps implement a security mechanism called X.509 certificate pinning that entails
checking if certificate on the server matches the expected one, thus requiring
a more invasive approach to see intercept communications with backend 
systems. Furthermore, there is more to the app functionality than what is 
visible on the GUI and within traffic logs. Certain mobile apps implement 
proprietary HTTP headers to make adversarial API integrations more difficult to
implement as they cannot be reverse engineered from intercepted API logs
alone.

We will rely on following software, all free to download:

* [Android Studio](https://developer.android.com/studio) - comprehensive IDE
for Android app development that ships with some tooling we will need. 
  * [ADB](https://developer.android.com/tools/adb) - CLI tool and communication
    interface to manage Android devices and emulators.
  * [avdmanager](https://developer.android.com/tools/avdmanager) - CLI tool
    to manage Android emulators.
* [mitmproxy](https://www.mitmproxy.org/) - MITM proxy server to intercept
network traffic (primarily API calls over HTTPS).
* [Frida](https://frida.re/) - dynamic instrumentation framework and toolkit.
Think of it as more powerful equivalent of `LD_PRELOAD`, but mostly meant for 
mobile app reversing.
* [rootAVD](https://gitlab.com/newbit/rootAVD) - Android emulator rooting tool
needed to get full access to system within emulator.

Combination of mitmproxy and Frida will allow us to tamper with both 
communications and computations of the app, thus enabling a far deeper insight
into inner workings than just sniffing API calls.

