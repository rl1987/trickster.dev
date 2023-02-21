+++
author = "rl1987"
title = "Understanding HTTP/2 fingerprinting"
date = "2023-02-28"
draft = true
tags = ["security"]
+++

Incoming HTTPS traffic can be fingerprinted by server-side systems to derive
technical characteristics of client hardware and software. One way to do this
is TLS fingerprinting that we have covered before on this blog and that
is commonly done by antibot vendors as part of automation countermeasures suite.
But that's not all they do. Fingerprinting can be done at HTTP/2 level as well.
Let us discuss HTTP/2 and how HTTP/2 fingerprinting works.

Unlike HTTP/1.1, HTTP/2 is a binary protocol, meaning it has binary wire format.
HTTP/1.1 requires a single TCP connection per request (with possibility for
connection reuse), but HTTP/2 supports request-response flow multiplexing across 
a single connection. Both of these things makes HTTP/2 more performant, less 
resource intensive protocol. Formal specification of HTTP/2 is 
[RFC 7540](https://www.rfc-editor.org/rfc/rfc7540). There is also something
called HPACK, which is HTTP/2 header compression technique, described in
[RFC 7541](https://www.rfc-editor.org/rfc/rfc7541). These two RFCs are primary
specs for HTTP/2. Theorethically HTTP/2 can be used for plaintext communications, 
but in practice it is pretty much always wrapped in TLS connection. Furtheremore,
HTTP/2 provides a way to implement a data-pushing from the server, whereas 
HTTP/1.1 assumes servers are completely reactive to client requests.

Conceptually speaking, HTTP/2 connection is a TCP connection that is further
divided into subconnections - streams. Streams are numbered logical 
bidirectional conversations between client and server. Stream 0 deals with
parameters for entire connection. Odd numbered streams should be initiated by 
the client and even numbered streams are started by the server. Each stream
in itself is a sequence of frames that it sent across a connection. HTTP/2
frame is a binary protocol data unit that contains stream ID, stream type, 
some Boolean flags and payload. In HTTP/2, a message (request or response) 
consists of a header frame and possibly some payload frames (there are no 
payload frames for GET request).


