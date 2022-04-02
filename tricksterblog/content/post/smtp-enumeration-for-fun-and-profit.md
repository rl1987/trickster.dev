+++
author = "rl1987"
title = "SMTP user enumeration for fun and profit"
date = "2022-04-02"
draft = true
tags = ["automation", "python", "growth-hacking", "security", "bug-bounties", "osint"]
+++

Sometimes it is desirable to enumerate all (or as much as possible) email recipients at given
domain. This can be done by establishing SMTP connection to corresponding mail server that
can be found via DNS MX record. 

There are three major approaches to do this:

* Using VRFY request that is meant to verify if there is user with corresponding mailbox on the server.
Server would respond with status code 250 if address is valid, 251 if it's not, 252 if it cannot be
determined.
* Using EXPN request that is meant to give a list of subscribers to a mailing list. Some email servers
consider every user to be in a list of single member, others do not. On success, server would respond 
with status code 250 and a list of subscribers in implementation-specific format.
* Using RCPT request that is designed to add one more recipient to the email being sent out. On success
the SMTP server would respond with status code 250 or 251. Note that [RFC 821](https://datatracker.ietf.org/doc/html/rfc821)
disallows more than 100 recipients being sent the same email message and that for some servers the limit may be
lower.

We will be primarily focusing on recipients that use Gmail/GSuite/Google Workspaces for their email service.
Let us use some Unix tools to manually check-and-verify some email addresses on domain peopledatalabs.com. 

As a first step, we need to find out a hostname of mail server for this domain. We use dig(1) for this:

```
$ dig -t MX peopledatalabs.com

; <<>> DiG 9.10.6 <<>> -t MX peopledatalabs.com
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 44234
;; flags: qr rd ra ad; QUERY: 1, ANSWER: 5, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 512
;; QUESTION SECTION:
;peopledatalabs.com.		IN	MX

;; ANSWER SECTION:
peopledatalabs.com.	3600	IN	MX	1 aspmx.l.google.com.
peopledatalabs.com.	3600	IN	MX	10 alt3.aspmx.l.google.com.
peopledatalabs.com.	3600	IN	MX	10 alt4.aspmx.l.google.com.
peopledatalabs.com.	3600	IN	MX	5 alt1.aspmx.l.google.com.
peopledatalabs.com.	3600	IN	MX	5 alt2.aspmx.l.google.com.

;; Query time: 66 msec
;; SERVER: 8.8.8.8#53(8.8.8.8)
;; WHEN: Sat Apr 02 13:50:38 EEST 2022
;; MSG SIZE  rcvd: 162

```

Now we can use NetCat to establish SMTP connection to SMTP server:

```
$ nc aspmx.l.google.com 25
220 mx.google.com ESMTP i23-20020a2ea237000000b002495e9ab777si3826740ljm.545 - gsmtp
```

Let us start SMTP transaction by sending HELO and MAIL FROM messages:

```
HELO test.example.org
250 mx.google.com at your service
MAIL FROM: <a@example.org>
250 2.1.0 OK i23-20020a2ea237000000b002495e9ab777si3826740ljm.545 - gsmtp
```

So far, so good. We're getting valid responses to our requests. Let us try sending VRFY
request to check an email address we know to be valid:

```
VRFY <support@peopledatalabs.com>
```

We get a response that is inconclusive and fails to give us an answer whether this address is valid:

```
252 2.1.5 Send some mail, I'll try my best i23-20020a2ea237000000b002495e9ab777si3826740ljm.545 - gsmtp
```

We get the same response if we try to verify a made up email address:

```
VRFY <fakefakefake@peopledatalabs.com>
252 2.1.5 Send some mail, I'll try my best i23-20020a2ea237000000b002495e9ab777si3826740ljm.545 - gsmtp
```

Thus we conclude that VRFY method is not applicable to enumerate addresses on Google-hosted email domains.

But what about EXPN method? Let us try it:

```
EXPN <support@peopledatalabs.com>
502 5.5.1 Unimplemented command. i23-20020a2ea237000000b002495e9ab777si3826740ljm.545 - gsmtp
```

This seems to be explicitly unsupported. Only RCPT method is left and it succeeds:

```
RCPT TO: <support@peopledatalabs.com>
250 2.1.5 OK i23-20020a2ea237000000b002495e9ab777si3826740ljm.545 - gsmtp
RCPT TO: <fakefakefake@peopledatalabs.com>
550-5.1.1 The email account that you tried to reach does not exist. Please try
550-5.1.1 double-checking the recipient's email address for typos or
550-5.1.1 unnecessary spaces. Learn more at
550 5.1.1  https://support.google.com/mail/?p=NoSuchUser i23-20020a2ea237000000b002495e9ab777si3826740ljm.545 - gsmtp
```

By using RCPT verb, we can conclusively verify if email address at Google-managed email domain is valid
or not.

Now let's try doing the same step in Python REPL with [dnspython](https://www.dnspython.org/) and smtplib modules:

```
>>> import dns.resolver
>>> answers = dns.resolver.resolve('peopledatalabs.com', 'MX')
>>> answers
<dns.resolver.Answer object at 0x109101910>
>>> answers[0]
<DNS IN MX rdata: 1 aspmx.l.google.com.>
>>> str(answers[0].exchange)
'aspmx.l.google.com.'
>>> conn = smtplib.SMTP(smtp_hostname)
>>> conn.helo('test.example.org')
(250, b'mx.google.com at your service')
>>> conn.mail('FROM: <a@example.org>')
(250, b'2.1.0 OK u30-20020ac25bde000000b00449fff281b7si4479810lfn.313 - gsmtp')
>>> conn.vrfy('support@peopledatalabs.com')
(252, b"2.1.5 Send some mail, I'll try my best u30-20020ac25bde000000b00449fff281b7si4479810lfn.313 - gsmtp")
>>> conn.vrfy('fakefakefake@peopledatalabs.com')
(252, b"2.1.5 Send some mail, I'll try my best u30-20020ac25bde000000b00449fff281b7si4479810lfn.313 - gsmtp")
>>> conn.expn('support@peopledatalabs.com')
(502, b'5.5.1 Unimplemented command. u30-20020ac25bde000000b00449fff281b7si4479810lfn.313 - gsmtp')
>>> conn.rcpt('support@peopledatalabs.com')
(250, b'2.1.5 OK u30-20020ac25bde000000b00449fff281b7si4479810lfn.313 - gsmtp')
>>> conn.rcpt('fakefakefake@peopledatalabs.com')
(550, b"5.1.1 The email account that you tried to reach does not exist. Please try\n5.1.1 double-checking the recipient's email address for typos or\n5.1.1 unnecessary spaces. Learn more at\n5.1.1  https://support.google.com/mail/?p=NoSuchUser u30-20020ac25bde000000b00449fff281b7si4479810lfn.313 - gsmtp")
>>> conn.quit()
(221, b'2.0.0 closing connection u30-20020ac25bde000000b00449fff281b7si4479810lfn.313 - gsmtp')
```



