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
but let's not go there now.

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
this kind of response (fields are 1 byte each): 

1. `VER` - must be 1 again.
2. `STATUS` - 0 iff auth succeeded, some other value otherwise.

Server closes the connection if client does not provide credentials that check
out.

Now we are ready to the real deal - establishing a connection to the remote
via proxy server. The client sends a request of the following wire format:

1. `VER` (1 octet) - protocol version (5).
2. `CMD` (1 octet) - command to the server (0x01 if we want to proxy a TCP
connection).
3. `RSV` (1 octet) - reserved, must be 0x00.
4. `ATYP` - address type:
   * 0x01 - IPv4
   * 0x03 - DNS hostname.
   * 0x04 - IPv6
5. `DST.ADDR` - destination address (in NBO); size depends on `ATYP`.
6. `DST.PORT` (2 octets) - destination port (in NBO).

The server will attempt to service the request. In typical use case `CMD` will
be 0x01 and that will be a CONNECT request asking the proxy to establish TCP
connection to remote host and bridge (splice) the TCP streams. 

When SOCKS server succeeds (or fails) to handle the request it will give one
last response:

1. `VER` - 0x05.
2. `REP` - reply field; 0x00 on success, error code on failure.
3. `RSV` - reserved, must be 0x00.
4. `ATYP` - address type.
5. `BND.ADDR` - address the server is bound to (e.g. exit IP of outbound 
connection).
6. `BND.PORT` - port of outbound connection.

If CONNECT request succeeded the client can now use the resulting two-legged 
connection as if it was a regular TCP connection - for all the remote server
knows it just got a fresh connection from a client and is ready to talk TLS or
some other protocol that is based on TCP transport. Furthermore, if remote
server is another SOCKS server it is possible to do a new SOCKS handshake for the
purpose of proxy chaining - extending the connection via one more proxy.

Besides the outbound TCP connection support, there are couple more slightly 
esoteric features SOCKS protocol has. One is BIND command (0x02) that lets
the client use SOCKS server for a secondary incoming connection. In that case
`BND.ADDR` and `BND.PORT` fields in the reply tell the client where in the 
network the port has been opened.

It is meant to be used with legacy FTP servers that work in active mode by 
establishing the second connection to transfer contents (files, directory 
listings) while leaving the original connection user originated available for 
new commands. Since the RFC requires the initial primary connection to be 
present for the lifetime of secondary connection this feature is not very useful
for anything else.

Second interesting, but not very used SOCKS feature is UDP support. If a client
sends UDP ASSOCIATE command (`CMD` = 0x03) the server may bind UDP port and setup
relaying of UDP datagrams. Since there is no such thing as connection at UDP level
and because it is desirable to retain the original port numbers in UDP datagrams
they are encapsulated in a wrapper message (defined in Section 7 of 
RFC 1928) when transferred between proxy and the client. 

Software projects supporting (subset of) SOCKS protocol:

* [Tor](https://www.torproject.org/) - overlay network for anonymous 
communications.
* [OpenSSH](https://www.openssh.com/) - SOCKS can be used over SSH tunnel. See
my previous post on SSH tips and tricks.
* [Curl](https://curl.se/) - see `--socks5`, `--proxy`, `--socks5-basic` CLI
options.
* Python requests module if [pysocks](https://github.com/Anorov/PySocks) is 
installed.
* Mitmproxy can be used in SOCKS5 mode (e.g. `mitmdump --mode socks5`).
