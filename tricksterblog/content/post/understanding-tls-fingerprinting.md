+++
author = "rl1987"
title = "Understanding TLS fingerprinting"
date = "2022-06-30"
draft = true
tags = ["security"]
+++

TLS (Transport Level Security) is a network protocol that sits between trasport layer (TCP)
and application layer protocols (HTTP, IMAP, SMTP and so on). It provides security features
such as encryption and authentication to TCP connections that merely deal with reliably
transferring streams of data. For example, a lot of URLs in modern web start with `https://`
and you typically see a lock icon by the address bar on your web browser. This indicates
TLS being used to not only encrypt data against passive sniffing by various adversaries, but
also against active MITM attacks that involve someone hijacking connection between
client and server for credential stealing and other nefarious purposes.

Exact details of TLS are fairly complex, but to encrypt data and authenticate the server it
has to perform a handshake. In TLS version 1.3 this is typically only one round trip:

1. Client send Client Hello message with a list of cipher suites it supports, proposed key
agreement protocol and some cryptographic materials to kickstart the encrypted communication
as soon as possible. Client Hello message may have a list of TLS extensions that provide
additional cryptographic capabilities and their parameters. Cipher suites are combinations
of cryptographic primitives (hashing and encryption functions) that will be very important
later on.

2. Server sends Server Hello message with the chosen key agreement protocol and their share
of keys and certificates.

3. When client receives the Server Hello message, it has everything to start encrypting
application-level protocol streams based on what it received in Server Hello message and
what it has computed before sending the Client Hello.

This description greatly oversimplifies all the details. The reader is encouraged to at least
skim [RFC 8446](https://www.rfc-editor.org/rfc/rfc8446.txt) to apreciate the complexity of
the protocol.

TLS 1.2 used to have a fairly elaborate dance between client and server to establish the connection.
There we separate steps for sending the certificates, sending each half of Diffie-Hellman
and so on. 

So what is the TLS fingerprinting? Well, it turns out that due to large number of fields
in Client Hello message it can become fairly unique to the software that it comes from.
Consider the following parts of Client Hello message:

* Exact TLS version (1.3 or 1.2 in non-legacy cases).
* Ciphersuites.
* TLS Extensions.
* (If Elliptic Curve Cryptography is used) elliptic curves and their parameters.

[Screenshot 1](/2022-06-27_15.31.57.png)

That's a lot of stuff and we have a bit of combinatorial explosion on the diversity
of Client Hello messages that could be created. Of course, not all combinations are
equally likely due to security reasons - some of the older ciphersuites are now
known to be insecure and should not longer be used.

So the thing is, programs tend to choose some unique combination of the above things.
There's one kind of Client Hello message that Google Chrome sends, another one for
Firefox, yet another one for curl and so on. Thus it is possible to develop a way
to fingerprint the Client Hello message and infer what kind of client that is.
A prominent implementation of TLS fingerprinting is [JA3](https://github.com/salesforce/ja3)
by Salesforce. In fact Salesforce even has a patent on TLS fingerprinting
(altough I have my doubts if they truly invented it). JA3 parses the Client
Hello message, extracts the fields that are relevant for fingerprinting, 
encodes them into a string and computes a MD5 hash from this string.
Since so many things in the message are unique to program acting as TLS
client the resulting hash will be unique as well. 

[Screenshot 2](/2022-06-27_15.26.05.png)

TLS fingerprinting is used not only to detect malware and network anomalies
but also as a countermeasure against automated traffic at CDN
level by CDN providers such as Akamai and Cloudflare (for enterprise
customer that have it enabled). So if there's HTTP request coming with all the
right headers that claims to be from Google Chrome, but TLS fingerprint
matches Python HTTP client the CDN knows that something is off and
rejects the request. Systems that implement TLS fingerprinting can keep
blacklists of known malicious clients and whitelists of known
good clients and update them as traffic is being monitored.

So what do we do about this as web scraper and automation developers?
Unfortunately Python requests module and standard libraries do not offer
much options to configure the low level TLS handshake details the way we
want. However there are some open source projects made for customising it
the way we need:

* [https://github.com/lwthiker/curl-impersonate](curl-impersonate) - 
a modified version of (lib)curl that is made to have the same TLS
fingerprints as many popular browsers.
* [utls](https://github.com/refraction-networking/utls) - a modified
version Golang's `crypto/tls` with extra customisability. You can set
the exact low-level details of Client Hello message when establishing
TLS connection.
* [TLS-Fingerprint-API](https://github.com/Carcraftz/TLS-Fingerprint-API) - a
proxy server developed to defeat TLS fingerprinting.

These projects provide ways to pretend to be a whitelisted TLS client or 
at least avoid being in a blacklist by manipualting the TLS fingerpint. 
Some developers working in darker shades of software development also 
implement Cipher Stunting - a technique that entails randomising 
fingerprintable parts of Client Hello message to further thwart the countermeasures.

If the target expects the traffic to come from a browser we could also
develop a solution based on browser automation by using something
like Playwright or Puppeteer.

[TODO: add some screenshots maybe]
