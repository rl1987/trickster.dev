+++
author = "rl1987"
title = "Setting up mitmproxy with Android"
date = "2022-01-23"
draft = true
tags = ["automation", "python", "security"]
+++

In the [previous post](/post/setting-up-mitmproxy-with-ios15/), instructions were provided on 
how to set up [mitmproxy](https://mitmproxy.org) with iOS device. In this one, we will be going
through setting up mitmproxy with Android device or emulator. If you would prefer to use Android
emulator for hacking mobile apps I would recommend [Genymotion](https://www.genymotion.com/) 
software which lets you create pre-rooted virtual devices. The following steps were reproduced with
Android 10 system running in Genymotion emulator with Google Chrome installed through ADB from 
some sketchy APK file that was found online.

Make sure your Android device or emulator is running in the same subnet as your computer. Install
and launch mitmproxy on your local computer. Find out the IP address of your local computer *in the
local subnet* and note it down. These things were discussed on greater detail in my previous post.

Now let us set things up on Android side. Open the Settings app and go to "Network & internet" ->
"Wi-Fi". Now press the settings (cog) icon next to the name of Wi-Fi network you are using. Press the
Edit (pen) icon on the top of the new screen. Explode the "Advanced options" entry in the modal window
and press the "None" text below "Proxy" label. Out of the 3 options, choose "Manual". Now you will be
given some textfields for proxy address and port. Under "Proxy hostname", enter the IP address of your
computer. In the "Proxy port" field, enter 8080. Leave everything else as-is and press Save.

Open Chrome in your Android system and go to [mitm.it](https://mitm.it). Press the green button under
Android label. A modal dialog will pop up and ask for certificate name - enter "mitmproxy" and press
"OK" button. Go back to Settings app and go to "Security" -> "Encryption and credentials" ->
"Trusted credentials". Verify that "mitmproxy" certificate is available in the User tab.

At this point, you should be seeing HTTP request intercepted and displayed on mitmproxy user interface.
The mitmproxy server is now performing the MITM attack by being in the middle of communications between
apps in Android device and remote backend server. This enables us to passively monitor the traffic
or actively mess with it.

If you would like this setup process to be automated, you may want to check out 
[mitmproxy.sh](https://gist.github.com/PhilippeBoisney/26eb5885668259325fd7bfe4dcda61b9) shell
script that uses Android Debug Bridge tool to push the CA certificate into Android system and set up
the proxy settings. Since it has some macOS-specific paths hardcoded it may not be useful right away,
but will provide you with a starting point.
