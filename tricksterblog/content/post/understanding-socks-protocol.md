+++
author = "rl1987"
title = "Understanding SOCKS protocol"
date = "2024-05-04"
tags = ["networking"]
draft = true
+++

In computer networking a proxy server is intermediate party (software that may or
may not be running on a separate server) to transfer application-level traffic
between client and the another server. There are two major ways this can be
accomplished: message forwarding (largely limited to plaintext HTTP) and 
connection tunneling. SOCKS is a widely utilised protocol that implements
the latter approach. Proxy servers may be useful for caching, load balancing, 
network traffic inspection, hiding real traffic source from target servers, 
bypassing censorship/geo-blocking and filtering the traffic. Today we will look
how SOCKS protocol works to relay the traffic between client and target server.

There are two major versions of SOCKS protocol: legacy SOCKS4A and slightly newer,
more advanced SOCKS5. Since SOCKS5 has some proper RFCs published to be used
as specifications it will be our primary focus. At macro level, primary purpose
of SOCKS5 protocol is to let user connect to a proxy server and provide a way to
"outsource" a secondary connection originating from proxy server and terminated
at the true destination the user wants to connect to. The original idea behind
this was enabling network firewalls to provide a controlled access to servers
running within private networks.

There are two document from IETF that we are most interested in:

1. [RFC 1928](https://datatracker.ietf.org/doc/html/rfc1928) - SOCKS Protocol 
Version 5.
2. [RFC 1929](https://datatracker.ietf.org/doc/html/rfc1929) - Username/Password 
Authentication for SOCKS V5.

Unlike many network protocol specifications, these are fairly short reads and
can be consumed in a single sitting.

One key thing to notice here is that SOCKS5 is a binary protocol - unlike HTTP 
it does not rely on human readable strings, but uses shorter binary messages.
The tradeoff here is that it uses bandwidth more efficiently at the expense of
making troubleshooting more difficult.

When client establishes a connection to SOCKS5 server it first is supposed to
send a version ID/method selection message with the following wire format:

1. `VER` (1 octet) - must be 5.
2. `NMETHODS` (1 octet) - how many auth methods will the client propose.
3. `METHODS` - a list of methods, represented by one octet each.

There are two auth methods that are of interest for us: no auth (0x00) and 
username/password auth (0x02). There's also GSSAPI being technically required, 
but let's no go there now.

So the following are valid examples of this message:

* `05 01 00` - client proposes doing connection without auth.
* `05 01 02` - client proposes using username/password based auth.
* `05 02 00 02` - client proposes either of the two and letting the server
choose.

Notice the TLV structure being used here: first we have "tag" - protocol version
number; next we have length - how many methods will be provided next and last
we have a list of methods. Structuring the wire format this way enables parsing
to be done incrementally.

Now the server has to make a choice if it wants to proceed with the connection
and respond with method selection consisting of two fields, one octet each:

1. `VER` - must be 5 again.
2. `METHOD` - either one of the proposed method values or 0xFF if all are 
rejected (connection is closed in that case).

If no-auth (0x00) is chosen the client is now allowed to proceed with using the 
proxying features of the server. But if username/password based auth is 
negotiated there is one extra thing left to do - the credential-based 
subnegotiation. Again, there are two messages being exchanged between client
and server. Client sends the username/password request of the following wire
format:

1. `VER` - must be 1.
2. `ULEN` - username length (without trailing NUL character if we're coding in C).
3. `UNAME` - username as ASCII string (`ULEN` octets).
4. `PLEN` - password length.
5. `PASSWD` - password.

Upon receipt of this message, server checks the credentials and responds with
this kind of response:

1. `VER` - must be 1 again.
2. `STATUS` - 0 iff auth succeeded, some other value otherwise.

Server closes the connection if client does not provide credentials that check
out.



