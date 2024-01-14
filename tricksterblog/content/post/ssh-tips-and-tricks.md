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

WRITEME

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

