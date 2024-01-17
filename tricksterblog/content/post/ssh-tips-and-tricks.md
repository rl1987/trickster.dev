+++
author = "rl1987"
title = "SSH tips and tricks"
date = "2024-01-15"
draft = true
tags = ["devops", "security", "automation"]
+++

SSH is well established protocol for securely accessing remote systems over the 
network for administration and devops purposes. A widely deployed OpenSSH 
software suite implements this protocol. But there is more to the SSH technology
than reaching a remote shell over ssh(1) or copying files via scp(1)/sftp(1).
We will go through some lesser known, somewhat advanced tricks and use cases
that could be valuable in your daily work.

SSH escape sequences
--------------------

Most people don't know that ssh(1) provides somewhat secret control sequences
that can be used to manage in-progress connections. Make sure the last keystroke
you have typed is Enter, then type the tilde character and question mark (`~?`).
You will be given the following message listing other sequences you can do in a
similar way:

```
Supported escape sequences:
 ~.   - terminate connection (and any multiplexed sessions)
 ~B   - send a BREAK to the remote system
 ~C   - open a command line
 ~R   - request rekey
 ~V/v - decrease/increase verbosity (LogLevel)
 ~^Z  - suspend ssh
 ~#   - list forwarded connections
 ~&   - background ssh (when waiting for connections to terminate)
 ~?   - this message
 ~~   - send the escape character by typing it twice
(Note that escapes are only recognized immediately after newline.)
```

`~C` gives you a secondary command prompt that can be used to manage port 
forwarding/tunneling (more on this later).

Single command through SSH
--------------------------

Sometimes you want to run just a single OS shell command via SSH connection
and get the output. That can be done with a standard SSH client by launching it
with `-t` and passing your command as last argument:

```
$ ssh -t root@167.172.24.25 "date -R"    
Sun, 14 Jan 2024 16:52:37 +0000
Connection to 167.172.24.25 closed.
```

2FA on SSH login
-----------------

Generally speaking, it is a recommended practice to use SSH keys for
authentication and to avoid relying on passwords. Passwordless SSH effectively 
prevents any successful brute force attack that could be done over the network.
However, if for some reason you still want to use SSH interface with 
password you can make it more secure by adding Two Factor Authentication step.
We will go through the steps that can be taken to set it up on Debian 12 system.

Make sure your APT cache is up to date and install `libpam-google-authenticator`
package through APT:

```
# apt-get install libpam-google-authenticator
```

Now we need to edit /etc/pam.d/sshd file to add the following line there:

```
auth required pam_google_authenticator.so
```

Also edit /etc/ssh/sshd\_config to make sure there's following lines there
(watch out for conflicting directives - you may need to change `no` to `yes` on
some lines):

```
UsePAM yes
ChallengeResponseAuthentication yes
KbdInteractiveAuthentication yes
AuthenticationMethods keyboard-interactive
```

Restart the sshd daemon to force it to read the updated config file:

```
# systemctl restart sshd.service
```

In your mobile device install Google Authenticator or a compatible app (e.g. 
[FreeOTP](https://freeotp.github.io/).

Now we're ready to run the `google-authenticator` tool, answer some questions and
follow the instructions:

```
# google-authenticator 

Do you want authentication tokens to be time-based (y/n) y
Warning: pasting the following URL into your browser exposes the OTP secret to Google:
  https://www.google.com/chart?chs=200x200&chld=M|0&cht=qr&chl=otpauth://totp/root@debian-s-1vcpu-512mb-10gb-ams3-01%3Fsecret%3D[REDACTED]%26issuer%3Ddebian-s-1vcpu-512mb-10gb-ams3-01
                                                                                                          
[REDACTED]

Your new secret key is: [REDACTED]
Enter code from app (-1 to skip): 371342
Code confirmed
Your emergency scratch codes are:
  [REDACTED]

Do you want me to update your "/root/.google_authenticator" file? (y/n) y

Do you want to disallow multiple uses of the same authentication
token? This restricts you to one login about every 30s, but it increases
your chances to notice or even prevent man-in-the-middle attacks (y/n) y

By default, a new token is generated every 30 seconds by the mobile app.
In order to compensate for possible time-skew between the client and the server,
we allow an extra token before and after the current time. This allows for a
time skew of up to 30 seconds between authentication server and client. If you
experience problems with poor time synchronization, you can increase the window
from its default size of 3 permitted codes (one previous code, the current
code, the next code) to 17 permitted codes (the 8 previous codes, the current
code, and the 8 next codes). This will permit for a time skew of up to 4 minutes
between client and server.
Do you want to do so? (y/n) y

If the computer that you are logging into isn't hardened against brute-force
login attempts, you can enable rate-limiting for the authentication module.
By default, this limits attackers to no more than 3 login attempts every 30s.
Do you want to enable rate-limiting? (y/n) y
```

We were given the option to either scan the QR code rendered on the terminal in
colored blocks or to Google chart feature to render it for us in the browser.

Once we do all of this, we will be asked both one time key and the password 
when logging in via SSH:

```
$ ssh root@178.62.232.185
(root@178.62.232.185) Verification code: 
(root@178.62.232.185) Password: 
```

SSH tunneling with `-L`
-----------------------

SSH connection as local SOCKS proxy
-----------------------------------

SSH-based Virtual Private Network
---------------------------------

Reaching SSH server behind nat via Tor Onion Service
----------------------------------------------------

Mounting directory subtree via sshfs
------------------------------------

Using SSH programmatically via paramiko
---------------------------------------

