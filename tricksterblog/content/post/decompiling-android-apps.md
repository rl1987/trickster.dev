+++
author = "rl1987"
title = "Decompiling Android apps"
date = "2022-08-02"
draft = true
tags = ["security", "reverse-engineering"]
+++

To get a deeper insight into how an Android app works we may want to convert the binary
form inside APK file to some sort of textual representation that we can read and edit.
This may be desirable for working out how to defeat some automation countermeasures
(e.g. HMAC being applied on API requests), finding vulnerabilities in the apps themselves
or in backend systems that service the apps, analysing malicious code and so on.
Reverse engineering uncovers the technical reality that is otherwise hidden and not
meant to be seen.

So what's an APK, in and of itself? Well, it turns out that APK is merely a Zip archive that we can unpack:

```
$ file "FirstNet Cybersecurity Aware_v1.2.5.0_apkpure.com.apk"
$ unzip FirstNet\ Cybersecurity\ Aware_v1.2.5.0_apkpure.com.apk 
$ ls -lh
total 30512
-rw-r--r--@  1 rl  staff    11K Dec 31  1979 AndroidManifest.xml
-rw-r--r--@  1 rl  staff    10M Aug  2 12:47 FirstNet Cybersecurity Aware_v1.2.5.0_apkpure.com.apk
drwxr-xr-x@ 70 rl  staff   2.2K Aug  2 14:21 META-INF
drwxr-xr-x@  3 rl  staff    96B Aug  2 14:21 assets
-rw-r--r--@  1 rl  staff   3.5M Dec 31  1979 classes.dex
-rw-r--r--@  1 rl  staff    68B Jan  1  1970 firebase-common.properties
-rw-r--r--@  1 rl  staff    78B Jan  1  1970 firebase-iid-interop.properties
-rw-r--r--@  1 rl  staff    62B Jan  1  1970 firebase-iid.properties
-rw-r--r--@  1 rl  staff    98B Jan  1  1970 firebase-measurement-connector.properties
-rw-r--r--@  1 rl  staff    74B Jan  1  1970 firebase-messaging.properties
drwxr-xr-x@ 86 rl  staff   2.7K Aug  2 14:21 kotlin
drwxr-xr-x@  6 rl  staff   192B Aug  2 14:21 lib
drwxr-xr-x@  3 rl  staff    96B Aug  2 14:21 okhttp3
-rw-r--r--@  1 rl  staff    74B Jan  1  1970 play-services-base.properties
-rw-r--r--@  1 rl  staff    82B Jan  1  1970 play-services-basement.properties
-rw-r--r--@  1 rl  staff    94B Jan  1  1970 play-services-cast-framework.properties
-rw-r--r--@  1 rl  staff    74B Jan  1  1970 play-services-cast.properties
-rw-r--r--@  1 rl  staff    76B Jan  1  1970 play-services-flags.properties
-rw-r--r--@  1 rl  staff    76B Jan  1  1970 play-services-stats.properties
-rw-r--r--@  1 rl  staff    76B Jan  1  1970 play-services-tasks.properties
drwxr-xr-x@ 57 rl  staff   1.8K Aug  2 14:21 res
-rw-r--r--@  1 rl  staff   974K Dec 31  1979 resources.arsc
```

After unpacking, we have some package metadata, app assets (images, XML documents, config files)
and a Dalvik Executable file classes.dex. You see, Android does not run a regular JVM even
though Android apps can still be written in Java. It runs Dalvik - a replacement for JVM that
is specifically designed for running it within mobile devices. Dalvik bytecode is different 
from regular JVM bytecode. Our objective is to turn Dalvik bytecode into something we can read.
Let us go through some tools that can help us with this.

[Apktool](https://ibotpeaches.github.io/Apktool/)
-------------------------------------------------

If Dalvik bytecode is essentially a binary machine code for the Dalvik VM, then there has
to be Dalvik assembly language that has one-to-one correspondence between language statement
and VM instruction. This language is called Smali and Apktool is a program to disassemble
Dalvik bytecode into Smali. Only a single command is needed to unpack APK and convert
classes.dex file into Smali source code:

```
$ apktool d "FirstNet Cybersecurity Aware_v1.2.5.0_apkpure.com.apk"  
```

In the new directory that Apktool creates there's smali directory that has subdirectories
according to Android package structure. The smali code looks something like this:

```smali
# instance fields
.field private final a:Lcom/squareup/picasso/r;

.field private final b:Lcom/squareup/picasso/O;


# direct methods
.method constructor <init>(Lcom/squareup/picasso/r;Lcom/squareup/picasso/O;)V
    .locals 0

    invoke-direct {p0}, Lcom/squareup/picasso/L;-><init>()V

    iput-object p1, p0, Lcom/squareup/picasso/A;->a:Lcom/squareup/picasso/r;

    iput-object p2, p0, Lcom/squareup/picasso/A;->b:Lcom/squareup/picasso/O;

    return-void
.end method
```

To make sense of this, we need to reference 
[Dalvik bytecode](https://source.android.com/devices/tech/dalvik/dalvik-bytecode.html)
page on the Android documentation portal. In this case, `invoke-direct` is an
instruction that calls a non-static Java or Kotlin method and `iput-object`
performs instance variable assignment. As we can see this is still relatively
high level code that is far easier to make sense of than x86 or ARM assembly.

We can edit the Smali code for our own purposes and use Apktool to rebuild the
modified version of the app. For example, a member of XDA Developers community
[patched](https://forum.xda-developers.com/t/camera-mod-armani-power-button-focusing-video-recording.777707/)
an app to get the hardware button events handled to his liking. 

[JADX](https://github.com/skylot/jadx)
--------------------------------------

But what if we want something closer to Java/Kotlin than assembly language?
JADX is another reverse engineering tool for reconstructing Java from Dalvik
bytecode to the extent that is possible. In most cases original symbol names
will be lost, but we will get a somewhat readable Java code from this.

There's CLI variant and GUI variant. Command for running the CLI variant 
is the following:

```
$ jadx FirstNet\ Cybersecurity\ Aware_v1.2.5.0_apkpure.com.apk 
```

To run GUI variant and get a graphical environment to browse the decompiled
source code run it like this:

```
$ jadx-gui FirstNet\ Cybersecurity\ Aware_v1.2.5.0_apkpure.com.apk 
```

[Screenshot 1](/2022-08-02_14.54.14.png)

[dex2jar](https://github.com/pxb1988/dex2jar)
---------------------------------------------

Dex2jar is a set of tools to deal with Dalvik bytecode. It is often used
to convert DEX file to JAR file that can be handled by many tools in Java
ecosystem. It does not perform decompilation by itself and is largely redundant
in the context of Apktool and JADX.

Android Studio
--------------

If you have Android Studio installed you can open APK file and get it disassembled
into Smali code without installing anything else. 

[Screenshot 2](/2022-08-02_15.04.06.png)
[Screenshot 3](/2022-08-02_15.04.44.png)

However Android Studio is fairly heavy piece of software and I would not install
it just for this purpose.

Some Android apps will be based on Android NDK and thus largely written in C or C++.
The above tools will not help in that case. One would need to use binary reverse
engineering tools such as IDA Pro, Ghidra or radare2.

