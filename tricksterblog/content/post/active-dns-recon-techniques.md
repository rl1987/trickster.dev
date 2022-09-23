+++
author = "rl1987"
title = "Active DNS recon techniques"
date = "2022-09-24"
draft = true
tags = ["security"]
+++

We discussed some [passive DNS recon techniques](passive-dns-recon-techniques/), but that's
only half of the store, as there is also active DNS reconnaissance that involves generating
actual DNS requests to gather data. Active DNS recon does not rely on information footprints
and secondary sources. Thus it enables us to get more up-to-date information on target systems.

So how do we send the DNS queries? We want to control what exact request we send and bypass
DNS caching on the local system, so using `getaddrinfo()` is out of question. 
Simplest way is to use nslookup(1) - a standard POSIX tool for doing DNS queries:

```
$ nslookup hackerone.com 8.8.8.8  
Server:		8.8.8.8
Address:	8.8.8.8#53

Non-authoritative answer:
Name:	hackerone.com
Address: 104.16.99.52
Name:	hackerone.com
Address: 104.16.100.52

$ nslookup -query="MX" hackerone.com 8.8.8.8
Server:		8.8.8.8
Address:	8.8.8.8#53

Non-authoritative answer:
hackerone.com	mail exchanger = 30 aspmx2.googlemail.com.
hackerone.com	mail exchanger = 20 alt1.aspmx.l.google.com.
hackerone.com	mail exchanger = 10 aspmx.l.google.com.
hackerone.com	mail exchanger = 30 aspmx3.googlemail.com.
hackerone.com	mail exchanger = 20 alt2.aspmx.l.google.com.

Authoritative answers can be found from:

```

We can differentiate between successful and failed queries by checking the return code. It 
will be 0 on success on 1 on failure. That can be useful when checking a list of gueesses for
subdomains in a shell script.

Another, more flexible tool to query DNS servers is dig(1). Depending on specifics of your exact
system you may need to install it separately. It provides the output in a different, more
machine readable form:

```
$ dig @8.8.8.8 hackerone.com

; <<>> DiG 9.10.6 <<>> @8.8.8.8 hackerone.com
; (1 server found)
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 16157
;; flags: qr rd ra; QUERY: 1, ANSWER: 2, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 512
;; QUESTION SECTION:
;hackerone.com.			IN	A

;; ANSWER SECTION:
hackerone.com.		300	IN	A	104.16.100.52
hackerone.com.		300	IN	A	104.16.99.52

;; Query time: 55 msec
;; SERVER: 8.8.8.8#53(8.8.8.8)
;; WHEN: Fri Sep 23 17:34:16 +07 2022
;; MSG SIZE  rcvd: 74

$ dig @8.8.8.8 -t MX hackerone.com

; <<>> DiG 9.10.6 <<>> @8.8.8.8 -t MX hackerone.com
; (1 server found)
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 7903
;; flags: qr rd ra; QUERY: 1, ANSWER: 5, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 512
;; QUESTION SECTION:
;hackerone.com.			IN	MX

;; ANSWER SECTION:
hackerone.com.		300	IN	MX	30 aspmx2.googlemail.com.
hackerone.com.		300	IN	MX	20 alt1.aspmx.l.google.com.
hackerone.com.		300	IN	MX	10 aspmx.l.google.com.
hackerone.com.		300	IN	MX	30 aspmx3.googlemail.com.
hackerone.com.		300	IN	MX	20 alt2.aspmx.l.google.com.

;; Query time: 48 msec
;; SERVER: 8.8.8.8#53(8.8.8.8)
;; WHEN: Fri Sep 23 17:34:40 +07 2022
;; MSG SIZE  rcvd: 172

```

If you code in Python you can use [dnspython](https://www.dnspython.org/) module for
performing DNS queries:

```
$ python3
Python 3.10.6 (main, Aug 30 2022, 04:58:14) [Clang 13.1.6 (clang-1316.0.21.2.5)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import dns.resolver
>>> resolver = dns.resolver.Resolver()
>>> resolver.nameservers = ['8.8.8.8']
>>> ans = resolver.resolve('hackerone.com')
>>> ans
<dns.resolver.Answer object at 0x1058cae30>
>>> ans.response
<DNS message, ID 55540>
>>> ans.response.answer
[<DNS hackerone.com. IN A RRset: [<104.16.100.52>, <104.16.99.52>]>]
>>> ans = resolver.resolve('hackerone.com', 'A')
>>> ans.response.answer
[<DNS hackerone.com. IN A RRset: [<104.16.100.52>, <104.16.99.52>]>]
>>> ans = resolver.resolve('hackerone.com', 'MX')
>>> ans.response.answer
[<DNS hackerone.com. IN MX RRset: [<30 aspmx2.googlemail.com.>, <20 alt1.aspmx.l.google.com.>, <10 aspmx.l.google.com.>, <30 aspmx3.googlemail.com.>, <20 alt2.aspmx.l.google.com.>]>]
```

We see that the data model of this library mirrors that of DNS protocol - there's a object
tree representing various layers/parts of a response.

We may want to perform a reverse DNS query that would give us a list of DNS names for a given
IP address. For example, there might a single web server belonging to web hosting company that
is hosting many websites, thus having multiple DNS addresses pointing to it. First we need to
convert IPv4 address to domain-namish form by appending `.in-addr.arpa`. Next, we launch a PTR
query:

```
$ dig @8.8.8.8 -t PTR 8.8.8.8.in-addr.arpa

; <<>> DiG 9.10.6 <<>> @8.8.8.8 -t PTR 8.8.8.8.in-addr.arpa
; (1 server found)
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 17913
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 512
;; QUESTION SECTION:
;8.8.8.8.in-addr.arpa.		IN	PTR

;; ANSWER SECTION:
8.8.8.8.in-addr.arpa.	18929	IN	PTR	dns.google.

;; Query time: 71 msec
;; SERVER: 8.8.8.8#53(8.8.8.8)
;; WHEN: Fri Sep 23 17:59:05 +07 2022
;; MSG SIZE  rcvd: 73

```

So given that we can launch DNS queries and they can yield some data on the target, how do
we perform this at larger scale? One way is DNS bruteforcing that entails using a wordlist to
generate possible subdomains (possibly by applying word permutations) and launching many DNS
 queries to check if they exist. Some tools to do this are:

* [Fierce](https://github.com/mschwager/fierce)
* [Amass](https://github.com/OWASP/Amass)
* [gobuster](https://github.com/OJ/gobuster)

Note that doing this will generate a lot of DNS requests that may crash your router, thus
it is recommended to launch these tools from VPS. Furthermore, it may not be enough to use
single DNS resolver like we did in earlier examples. When using multiple DNS resolvers, there's
a potential issue of data reliability. [DNSValidator](https://github.com/vortexau/dnsvalidator)
is a tool that takes a long list of DNS servers, runs test queries on them and over time narrows
down the list to a subset of reliable servers.

Furthemore, if we know of one subdomain, e.g. dev.example.org we may suppose that numbered
variants, such as dev1.example.org also exist. DNS alteration scanning is automated process of
checking for these kind of subdomains. [Altdns](https://github.com/infosec-au/altdns) is open
source tool that implements this technique.

So far we discussed launching DNS requests to learn about the target, but did not touch anything
that interacts with the target. Yet another way to gather target subdomains is to crawl across
the site and scrape them from the links or Javascript snippets. This would be fairly trivial 
to implement with Scrapy, but there are some ready-made tools to do this:

* [hakrawler](https://github.com/hakluke/hakrawler)
* [Gospider](https://github.com/jaeles-project/gospider)

DNS zone transfer is mechanism to transfer DNS records between servers. It can be either
authoritative that relies on AXFR sub-protocol or incremental that relies on IXFR.
For recon purposes the feasibility of doing this relies on misconfigured access control
on DNS server, which is not that common in modern world and should not be relied upon. 
There is a deliberately insecure DNS server that can be used to demonstrate this
kind of vulnerability:

```
$ dig axfr @nsztm1.digi.ninja zonetransfer.me

; <<>> DiG 9.10.6 <<>> axfr @nsztm1.digi.ninja zonetransfer.me
; (1 server found)
;; global options: +cmd
zonetransfer.me.	7200	IN	SOA	nsztm1.digi.ninja. robin.digi.ninja. 2019100801 172800 900 1209600 3600
zonetransfer.me.	300	IN	HINFO	"Casio fx-700G" "Windows XP"
zonetransfer.me.	301	IN	TXT	"google-site-verification=tyP28J7JAUHA9fw2sHXMgcCC0I6XBmmoVi04VlMewxA"
zonetransfer.me.	7200	IN	MX	0 ASPMX.L.GOOGLE.COM.
zonetransfer.me.	7200	IN	MX	10 ALT1.ASPMX.L.GOOGLE.COM.
zonetransfer.me.	7200	IN	MX	10 ALT2.ASPMX.L.GOOGLE.COM.
zonetransfer.me.	7200	IN	MX	20 ASPMX2.GOOGLEMAIL.COM.
zonetransfer.me.	7200	IN	MX	20 ASPMX3.GOOGLEMAIL.COM.
zonetransfer.me.	7200	IN	MX	20 ASPMX4.GOOGLEMAIL.COM.
zonetransfer.me.	7200	IN	MX	20 ASPMX5.GOOGLEMAIL.COM.
zonetransfer.me.	7200	IN	A	5.196.105.14
zonetransfer.me.	7200	IN	NS	nsztm1.digi.ninja.
zonetransfer.me.	7200	IN	NS	nsztm2.digi.ninja.
_acme-challenge.zonetransfer.me. 301 IN	TXT	"6Oa05hbUJ9xSsvYy7pApQvwCUSSGgxvrbdizjePEsZI"
_sip._tcp.zonetransfer.me. 14000 IN	SRV	0 0 5060 www.zonetransfer.me.
14.105.196.5.IN-ADDR.ARPA.zonetransfer.me. 7200	IN PTR www.zonetransfer.me.
asfdbauthdns.zonetransfer.me. 7900 IN	AFSDB	1 asfdbbox.zonetransfer.me.
asfdbbox.zonetransfer.me. 7200	IN	A	127.0.0.1
asfdbvolume.zonetransfer.me. 7800 IN	AFSDB	1 asfdbbox.zonetransfer.me.
canberra-office.zonetransfer.me. 7200 IN A	202.14.81.230
cmdexec.zonetransfer.me. 300	IN	TXT	"; ls"
contact.zonetransfer.me. 2592000 IN	TXT	"Remember to call or email Pippa on +44 123 4567890 or pippa@zonetransfer.me when making DNS changes"
dc-office.zonetransfer.me. 7200	IN	A	143.228.181.132
deadbeef.zonetransfer.me. 7201	IN	AAAA	dead:beaf::
dr.zonetransfer.me.	300	IN	LOC	53 20 56.558 N 1 38 33.526 W 0.00m 1m 10000m 10m
DZC.zonetransfer.me.	7200	IN	TXT	"AbCdEfG"
email.zonetransfer.me.	2222	IN	NAPTR	1 1 "P" "E2U+email" "" email.zonetransfer.me.zonetransfer.me.
email.zonetransfer.me.	7200	IN	A	74.125.206.26
Hello.zonetransfer.me.	7200	IN	TXT	"Hi to Josh and all his class"
home.zonetransfer.me.	7200	IN	A	127.0.0.1
Info.zonetransfer.me.	7200	IN	TXT	"ZoneTransfer.me service provided by Robin Wood - robin@digi.ninja. See http://digi.ninja/projects/zonetransferme.php for more information."
internal.zonetransfer.me. 300	IN	NS	intns1.zonetransfer.me.
internal.zonetransfer.me. 300	IN	NS	intns2.zonetransfer.me.
intns1.zonetransfer.me.	300	IN	A	81.4.108.41
intns2.zonetransfer.me.	300	IN	A	167.88.42.94
office.zonetransfer.me.	7200	IN	A	4.23.39.254
ipv6actnow.org.zonetransfer.me.	7200 IN	AAAA	2001:67c:2e8:11::c100:1332
owa.zonetransfer.me.	7200	IN	A	207.46.197.32
robinwood.zonetransfer.me. 302	IN	TXT	"Robin Wood"
rp.zonetransfer.me.	321	IN	RP	robin.zonetransfer.me. robinwood.zonetransfer.me.
sip.zonetransfer.me.	3333	IN	NAPTR	2 3 "P" "E2U+sip" "!^.*$!sip:customer-service@zonetransfer.me!" .
sqli.zonetransfer.me.	300	IN	TXT	"' or 1=1 --"
sshock.zonetransfer.me.	7200	IN	TXT	"() { :]}; echo ShellShocked"
staging.zonetransfer.me. 7200	IN	CNAME	www.sydneyoperahouse.com.
alltcpportsopen.firewall.test.zonetransfer.me. 301 IN A	127.0.0.1
testing.zonetransfer.me. 301	IN	CNAME	www.zonetransfer.me.
vpn.zonetransfer.me.	4000	IN	A	174.36.59.154
www.zonetransfer.me.	7200	IN	A	5.196.105.14
xss.zonetransfer.me.	300	IN	TXT	"'><script>alert('Boo')</script>"
zonetransfer.me.	7200	IN	SOA	nsztm1.digi.ninja. robin.digi.ninja. 2019100801 172800 900 1209600 3600
;; Query time: 232 msec
;; SERVER: 81.4.108.41#53(81.4.108.41)
;; WHEN: Fri Sep 23 18:53:56 +07 2022
;; XFR size: 50 records (messages 1, bytes 1994)
```

We see that all records have been dumped without us needing to query them one-by-one.

If DNSSEC is deployed, NSEC records would exist and conveniently provide subdomains for us.
Each NSEC points to next subdomain in DNS zone (a portion of DNS namespace managed by
single admin/organisation) in a way that forms a linked list. Traversal of this list gives
us a list of subdomains. This is known as DNS zone walking.

Some tools that can automate this technique:

* [DNSrecon](https://github.com/darkoperator/dnsrecon)
* dnssecwalk from [thc-ipv6](https://github.com/vanhauser-thc/thc-ipv6) toolkit.

