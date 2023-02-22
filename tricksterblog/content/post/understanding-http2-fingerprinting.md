+++
author = "rl1987"
title = "Understanding HTTP/2 fingerprinting"
date = "2023-02-28"
draft = true
tags = ["security"]
+++

Incoming HTTPS traffic can be fingerprinted by server-side systems to derive
technical characteristics of client side systems. One way to do this
is TLS fingerprinting that we have covered before on this blog and that
is commonly done by antibot vendors as part of automation countermeasures suite.
But that's not all they do. Fingerprinting can be done at HTTP/2 level as well.
Let us discuss HTTP/2 and how HTTP/2 fingerprinting works. More specifically,
we will look into HTTP/2 fingerprinting technique that was proposed by Akamai.

Unlike HTTP/1.1, HTTP/2 is a binary protocol, meaning it has binary wire format.
HTTP/1.1 requires a single TCP connection per request (with possibility for
connection reuse), but HTTP/2 supports request-response flow multiplexing across 
a single connection. Both of these things makes HTTP/2 more performant, less 
resource intensive protocol. Formal specification of HTTP/2 is 
[RFC 7540](https://www.rfc-editor.org/rfc/rfc7540). There is also something
called HPACK, which is HTTP/2 header compression technique, described in
[RFC 7541](https://www.rfc-editor.org/rfc/rfc7541). These two RFCs are primary
specs for HTTP/2. Theorethically HTTP/2 can be used for plaintext communications, 
but in practice it is pretty much always wrapped in TLS connection. When TLS
connection is established, TLS ALPN (Application Level Protocol Negotiation)
extension is used to negotiate whether to use HTTP/1.1 or HTTP/2 in the 
encrypted channel.

Conceptually speaking, HTTP/2 connection is a TCP/TLS connection that is further
divided into subconnections - streams. Streams are numbered logical 
bidirectional conversations between client and server. Stream 0 deals with
parameters for entire connection. Odd numbered streams should be initiated by 
the client and even numbered streams are started by the server. Each stream
in itself is a sequence of frames that it sent across a connection. HTTP/2
frame is a binary protocol data unit that contains stream ID, stream type, 
some Boolean flags and payload. There are ten possible frame types. 
Most significant are HEADERS and DATA. In HTTP/2, a message consists of
consists of a HEADERS frame and possibly some DATA frames with payload (there 
are no payload frames for GET request). Other types of frames deal with stream
priorities, flow control and so on. After the TLS connection is established,
SETTINGS frames are exchanged to negotiate some initial parameters for data
exchange.

HTTP/2 fingerprinting entails observing behaviour of the client to infer various
attributes about software (OS, browser, etc.) on the client side system. It
does not uniquely identify the end user. HTTP/2 fingerprinting can be 
implemented at web server or content delivery network. Client behaviour is
observed when connection is being established. Fingerprinting solution gathers
data on initial connection settings, flow control, stream priorities and
pseudo header ordering to deduce things from that.

First component of fingerprint comes from SETTINGS frame that client has sent for
the zeroth stream. Default values of various parameters that client proposes 
vary between HTTP/2 client implementations - Firefox consistently sends one 
set of parameter, Chrome another set and so on. Furthermore, these setting may
vary between browser versions, which is potentially another piece of infromation
that can be inferred. More specifically, SETTINGS frame sets the following
parameters:

* `SETTINGS_HEADER_TABLE_SIZE` - size of header compression table (in bytes)
* `SETTINGS_ENABLE_PUSH` - allow or disallow data pushing from the server 
(disabled in modern Chrome).
* `SETTINGS_MAX_CONCURRENT_STREAMS` - maximum number of concurrent streams.
* `SETTINGS_INITIAL_WINDOW_SIZE` - initial stream window size (e.g. how many 
bytes can be in-flight between client and server).
* `SETTINGS_MAX_FRAME_SIZE` - how big the frames are allowed to get (in bytes).
* `SETTINGS_MAX_HEADER_LIST_SIZE` - advisory upper limit for header size.

To make a part of fingerprint, SETTINGS frame is parsed and settings ID-value
pairs are extracted.

Second part comes from WINDOW\_UPDATE frame that is commonly sent by many clients
when starting a connection. If this frame was sent, the window size value is
appended to the fingerprint. If not, 0 is appended instead.

Third component comes from PRIORITY frames. An interesting feature of HTTP/2 is
that it allows setting not only stream priorities, but also dependencies between
streams. Streams are arranged in a tree structure, stream 0 being the root node.
Child nodes from node 0 are streams that are dependent on it and they can have
their own dependent streams down the tree. This provides some additional
entropy for fingerprinting. All of this allow client to communicate it's
preferences for resource allocation across streams. Some HTTP/2 clients start
sending the PRIORITY frames to do so early in the connection. Each PRIORITY 
frame has two stream IDs (for parent and child streams), priority weight and 
an exclusivity bit. These numbers are also included into the fingerprint.

Fourth and the last component of fingerprint is pseudo header ordering.
Pseudo headers are binary, non optional parts of HEADERS frame - `:method`,
`:authority`, `:scheme`, `:path` that have their own equivalents in HTTP/1.1
headers and ordering that is implementation-specific, thus providing a signal
of what kind of software sent the request. For instance, Chrome has one
particular ordering hardcoded, Firefox another one and so forth.

The final fingerprint string comprises of pipe-separated four substrings,
each representing one of the above components. This string can be further
passed into a hash function. You can check your own HTTP/2 (and TLS) 
fingerprints at [tls.peet.ws](https://tls.peet.ws).

HTTP/2 is commonly used for security purposes, such as fighting automation.
It is part of toolkit in automation countermeasures arsenal that companies
such as Akamai are selling to their customers.

To see an example of this kind of fingerprinting you may want to check Xetera's
modified version of nginx, especially the [`calculate_fingerprint()` function
in src/http/v2/ngx\_http\_v2\_module.c](https://github.com/Xetera/nginx-http2-fingerprint/blob/master/src/http/v2/ngx_http_v2_module.c#L243).

As scraper/bot developers, how do we deal with something like this? Well,
the key is to make sure that HTTP/2 traffic we generate has all the 
aforementioned traits to be exactly the same as one of the mainstream browsers. 
There are some open source project that help with that:

* curl-impersonate is a modified version of curl that pretends to be a browser
by emitting TLS/HTTP2 traffic that is consistent with browser fingerprints.
* [fhttp](https://github.com/useflyent/fhttp) is a Golang HTTP client library
that can help with this as well (there's some forks for this repo that 
introduce further work).
* [tls-client](https://github.com/bogdanfinn/tls-client) - Golang library that
addresses TLS and HTTP/2 client fingerprinting (based on fhttp).
