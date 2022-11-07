+++
author = "rl1987"
title = "Axiom: just-in-time dynamic infra for offensive security operations"
date = "2022-11-08"
draft = true
tags = ["security", "bug-bounties"]
+++

When doing recon part of penetration testing or bug bounty hunting engagements one
may want to run various tools (such as port scanners, crawlers, vulnerability scanners,
headless browsers and so on) in a VPS environment that will no longer be needed when
the task at hand is complete. For large-scale scanning it is highly desirable to spread
the workload across many servers. To address these need, [axiom](https://github.com/pry0cc/axiom)
was developed. Axiom is a dynamic infrastructure framework designed for quick setup and
teardown of reproducible infrastructure. 

0xtavian, one of the founding developers of this project, was doing security work and
has found that there's a great variety of security tools, but no established way to 
use them in unified way to easily set up an VPS for hacking. Furthermore, security
centric Linux distros such as Kali provided a variety of tools out of the box, but
lacked tooling for truly scalable bounty hunting and pentesting. These two problems
motivated 0xtavian to create Axiom with pry0cc, another developer in security space.

Let us install Axiom into VPS instance running one of the operating systems
that support the easy install:

* Debian Linux
* Ubuntu Linux
* Kali Linux
* Windows (with Ubuntu on WSL)
* macOS

I am recommending doing this in a VPS environment because Axiom installs some
packages on your local system through APT or Homebrew that you may not need otherwise.
Furthermore, you may want to run Axiom scans in tmux session on the server for longer
scans that may take overnight or multiple days.

The easy install command is the following:

```bash
bash <(curl -s https://raw.githubusercontent.com/pry0cc/axiom/master/interact/axiom-configure)
```

This will download Axiom source code, install dependencies, establish API connection to
cloud provider (Digital Ocean, Linode, Azure, IBM Cloud or AWS) - you will be asked to provide
API credentials for your cloud providers, as well as some other details - and use Packer to create
VPS image with all the tooling to be used for scanning. For the purpose of trying it out choose 
the default provisioner.

Once installation is complete, let us start small by setting up a single VPS with `axiom-init`
command (this should take a few minutes):

```
$ axiom-init first
Initializing 'first' at 'lon1' with image 'axiom-default-1666592377'
INITIALIZING IN 5 SECONDS, CTRL+C to quit... 
Initialized instance 'first' at '[REDACTED]'!
To connect, run 'axiom-ssh first' or 'axiom-connect'
```

Now let us run a single command through `axiom-exec` on the worker server:

```
$ axiom-exec 'dig google.com'
=====================================================
Interlace v1.9.6	by Michael Skelton (@codingo_)
                  	& Sajeeb Lohani (@sml555_)
=====================================================
  0%|                                                                                                                                                                                 | 0/1 [00:00<?, ?it/s][11:19:50] [THREAD] [ssh -F /root/.axiom/tmp/exec/axiom-exec+1667819982/sshconfig -o StrictHostKeyChecking=no -o PasswordAuthentication=no first 'tmux new -d -s axiom-exec+1667819982 && tmux send-keys -t axiom-exec+1667819982 "bash -i /tmp/exec/axiom-exec+1667819982/command  > >(tee -a /tmp/exec/axiom-exec+1667819982/stdout.log) 2> >(tee -a /tmp/exec/axiom-exec+1667819982/stderr.log >&2) ; touch /tmp/exec/axiom-exec+1667819982/first" ENTER ' "&& tmux send-keys -t axiom-exec+1667819982 exit ENTER"] Added to Queue 
100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 16.72it/s]

; <<>> DiG 9.16.1-Ubuntu <<>> google.com
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 7177
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 65494
;; QUESTION SECTION:
;google.com.			IN	A

;; ANSWER SECTION:
google.com.		31	IN	A	142.250.187.206

;; Query time: 0 msec
;; SERVER: 127.0.0.53#53(127.0.0.53)
;; WHEN: Mon Nov 07 11:19:50 UTC 2022
;; MSG SIZE  rcvd: 55


```

Axiom ships with bunch of recipes (modules) that integrate various scanning tools into the system.
Let us try running Nmap on the worker server. First, we need to create an input file
with target hostname(s):

```
$ echo "scanme.nmap.org" >> target.txt
```

Then we can run `axiom-scan` to run a scan with Nmap module and our text file as input:

```
$ axiom-scan target.txt -m nmap -o nmap_out.txt -oG nmap_out.txt
sorting and greping unique for: 'nmap_out.txt'
              _
  ____ __  __(_)___  ____ ___        ______________ _____
 / __ `/ |/_/ / __ \/ __ `__ \______/ ___/ ___/ __ `/ __ \
/ /_/ />  </ / /_/ / / / / / /_____(__  ) /__/ /_/ / / / /
\__,_/_/|_/_/\____/_/ /_/ /_/     /____/\___/\__,_/_/ /_/

                                    @pry0cc
                                 & @0xtavian

creating scan working directory at : /home/op/scan/nmap+166782070320617/
module: [ nmap ] | module args: [  ] | input: [ 1 lines ] |
instances:  1  [ first ] |
command: [ sudo nmap -iL input -oG output ] | ext: [ txt ] | threads: [ null ]
spliting and distributing input file...
[ OK ]
Starting Nmap 7.92 ( https://nmap.org ) at 2022-11-07 11:31 UTC
Stats: 0:00:00 elapsed; 0 hosts completed (0 up), 1 undergoing Ping Scan
Ping Scan Timing: About 100.00% done; ETC: 11:31 (0:00:00 remaining)
Nmap scan report for scanme.nmap.org (45.33.32.156)
Host is up (0.15s latency).
Other addresses for scanme.nmap.org (not scanned): 2600:3c01::f03c:91ff:fe18:bb2f
Not shown: 996 closed tcp ports (reset)
PORT      STATE SERVICE
22/tcp    open  ssh
80/tcp    open  http
9929/tcp  open  nping-echo
31337/tcp open  Elite

Nmap done: 1 IP address (1 host up) scanned in 2.53 seconds
first scan finished
Mode set to txt.. Sorting unique.
Appending axiom-scan runtime statistics to : /root/.axiom/stats.log
module: [ nmap ] | module args: [  ] | instances: [ 1 ] | targets: [ 1 targets ] | results: [ 4 results ] |
runtime: [ 00h:00m:41s ] | date: [ Mon Nov  7 11:31:43 UTC 2022 ] | id: [ nmap+166782070320617 ] |
output: [ /root/nmap_out.txt ] | log: [ /root/.axiom/logs/nmap+166782070320617 ] | remote: [ /home/op/scan/nmap+166782070320617 ]  |
command: [ sudo nmap -iL input -oG output ] | ext: [ txt ] | threads: [ null ]
```

We used `-m` to select an Axiom module and `-o` for output file. After that, we can
pass the CLI arguments to the tool that Axiom would run - we used `-oG` for selecting
a greppable output.

To list currently running instances, we can run `axiom-ls`. To make a backup of an instance,
we can use `axiom-backup` with the name of an instance (to be restored using `axiom-restore`).

But for now, we want to simply remove an instance we have created. We are doing this with
`axiom-rm`:

```
$ axiom-rm first
Deleting 'first'...
Warning: Are you sure you want to delete this Droplet? (y/N) ? y
```

Now we want to go bigger. To fully benefit from Axiom we want to create a fleet - 
a set of worker servers that will perform the workloads in a load-balanced
way. Let us create a fleet of 8 servers.

```
$ axiom-fleet -i 8
```

We will try running some scans against [Firing Range](https://public-firing-range.appspot.com/) - a deliberately insecure
website developed for testing web security scanners. Let us put the corresponding
URL to target.txt file:

```
$ echo "https://public-firing-range.appspot.com/" > target.txt 
```

To crawl the site and save all the page URLs into a textfile, let us run
[Hakrawler](https://github.com/hakluke/hakrawler) through Axiom:

```
$ axiom-scan target.txt -m hakrawler -o crawl.txt
```

That gave us a list of 287 URLs:

```
$ wc -l crawl.txt 
287 crawl.txt
```

This new list can be used as input file for the next scan that will entail running
[Nuclei](https://github.com/projectdiscovery/nuclei) vulnerability scanner: 

```
$ axiom-scan crawl.txt -m nuclei -o nuclei.txt
```

Axiom now splits the input file into even parts across all worker server so that workload
is distributed evenly, runs Nuclei on them via SSH, waits for it to finish, downloads the
results, deduplicates them and saves into a textfile. Large scans can take a while even
when done across several servers, thus I recommend doing them from a tmux session.

There will be quite a bit of verbose output in the terminal that mostly matters for
seeing progress and troubleshooting, thus is not reproduced here. What matters is stuff
in the output file. Not everything here is something that warrants further attention,
but some of the entries will be marked as medium or high in severity and in real 
engagement would need to be investigated further. 

To remove the fleet, we can use `axiom-rm` with server name prefix:

```
$ axiom-rm 'kalam*" -f
```

To daisy-chain several scans into larger workload one can trivially write a Bash
script consisting of Axiom commands in the order you would run them on the shell.

