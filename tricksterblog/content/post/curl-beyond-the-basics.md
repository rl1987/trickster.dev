+++
author = "rl1987"
title = "cURL beyond the basics"
date = "2022-09-07"
draft = true
tags = ["curl"]
+++

Curl is a prominent CLI tool and library for performing client-side
requests in a number of application layer protocols. Commonly it is used
for HTTP requests. However, there is more to curl than that. We will 
go through some less known features of curl that can be used in web
scraping and automation systems.

Debugging
---------

Sometimes things fail and require us to take a deeper look into technical
details of what is happening. Running curl with `--verbose` (or just `-v`) 
gives us a certain level of technical details regarding connection establishment
and protocol messages being transmitted:

```
$ curl http://httpbin.org/status/401 -v 
*   Trying 34.227.213.82:80...
* Connected to httpbin.org (34.227.213.82) port 80 (#0)
> GET /status/401 HTTP/1.1
> Host: httpbin.org
> User-Agent: curl/7.79.1
> Accept: */*
> 
* Mark bundle as not supporting multiuse
< HTTP/1.1 401 UNAUTHORIZED
< Date: Sat, 03 Sep 2022 07:28:47 GMT
< Server: gunicorn/19.9.0
< WWW-Authenticate: Basic realm="Fake Realm"
< Access-Control-Allow-Origin: *
< Access-Control-Allow-Credentials: true
< Cache-Control: proxy-revalidate
< Content-Length: 0
< Connection: Keep-Alive
< 
* Connection #0 to host httpbin.org left intact
```

However, we may want to look deeper. There are CLI options that gives us even
more detailed output for troubleshooting. `--trace` saves full dump of data
being sent and received into a text file (or standard output if we use `-`
instead of file path):

```
$ curl http://httpbin.org/status/401 --trace -
== Info:   Trying 34.227.213.82:80...
== Info: Connected to httpbin.org (34.227.213.82) port 80 (#0)
=> Send header, 85 bytes (0x55)
0000: 47 45 54 20 2f 73 74 61 74 75 73 2f 34 30 31 20 GET /status/401 
0010: 48 54 54 50 2f 31 2e 31 0d 0a 48 6f 73 74 3a 20 HTTP/1.1..Host: 
0020: 68 74 74 70 62 69 6e 2e 6f 72 67 0d 0a 55 73 65 httpbin.org..Use
0030: 72 2d 41 67 65 6e 74 3a 20 63 75 72 6c 2f 37 2e r-Agent: curl/7.
0040: 37 39 2e 31 0d 0a 41 63 63 65 70 74 3a 20 2a 2f 79.1..Accept: */
0050: 2a 0d 0a 0d 0a                                  *....
== Info: Mark bundle as not supporting multiuse
<= Recv header, 27 bytes (0x1b)
0000: 48 54 54 50 2f 31 2e 31 20 34 30 31 20 55 4e 41 HTTP/1.1 401 UNA
0010: 55 54 48 4f 52 49 5a 45 44 0d 0a                UTHORIZED..
<= Recv header, 37 bytes (0x25)
0000: 44 61 74 65 3a 20 53 61 74 2c 20 30 33 20 53 65 Date: Sat, 03 Se
0010: 70 20 32 30 32 32 20 30 37 3a 33 36 3a 32 35 20 p 2022 07:36:25 
0020: 47 4d 54 0d 0a                                  GMT..
<= Recv header, 25 bytes (0x19)
0000: 53 65 72 76 65 72 3a 20 67 75 6e 69 63 6f 72 6e Server: gunicorn
0010: 2f 31 39 2e 39 2e 30 0d 0a                      /19.9.0..
<= Recv header, 44 bytes (0x2c)
0000: 57 57 57 2d 41 75 74 68 65 6e 74 69 63 61 74 65 WWW-Authenticate
0010: 3a 20 42 61 73 69 63 20 72 65 61 6c 6d 3d 22 46 : Basic realm="F
0020: 61 6b 65 20 52 65 61 6c 6d 22 0d 0a             ake Realm"..
<= Recv header, 32 bytes (0x20)
0000: 41 63 63 65 73 73 2d 43 6f 6e 74 72 6f 6c 2d 41 Access-Control-A
0010: 6c 6c 6f 77 2d 4f 72 69 67 69 6e 3a 20 2a 0d 0a llow-Origin: *..
<= Recv header, 40 bytes (0x28)
0000: 41 63 63 65 73 73 2d 43 6f 6e 74 72 6f 6c 2d 41 Access-Control-A
0010: 6c 6c 6f 77 2d 43 72 65 64 65 6e 74 69 61 6c 73 llow-Credentials
0020: 3a 20 74 72 75 65 0d 0a                         : true..
<= Recv header, 33 bytes (0x21)
0000: 43 61 63 68 65 2d 43 6f 6e 74 72 6f 6c 3a 20 70 Cache-Control: p
0010: 72 6f 78 79 2d 72 65 76 61 6c 69 64 61 74 65 0d roxy-revalidate.
0020: 0a                                              .
<= Recv header, 19 bytes (0x13)
0000: 43 6f 6e 74 65 6e 74 2d 4c 65 6e 67 74 68 3a 20 Content-Length: 
0010: 30 0d 0a                                        0..
<= Recv header, 24 bytes (0x18)
0000: 43 6f 6e 6e 65 63 74 69 6f 6e 3a 20 4b 65 65 70 Connection: Keep
0010: 2d 41 6c 69 76 65 0d 0a                         -Alive..
<= Recv header, 2 bytes (0x2)
0000: 0d 0a                                           ..
== Info: Connection #0 to host httpbin.org left intact
```

If we wanted to skip hexdumps of protocol messages we can use `--trace-ascii`
instead of `--trace`. To augment the debug output with timing information
we can use `--trace-time`:

```
$ curl http://httpbin.org/status/401 --trace-ascii - --trace-time
14:38:54.540384 == Info:   Trying 54.147.68.244:80...
14:38:54.573724 == Info: Connected to httpbin.org (54.147.68.244) port 80 (#0)
14:38:54.573928 => Send header, 85 bytes (0x55)
0000: GET /status/401 HTTP/1.1
001a: Host: httpbin.org
002d: User-Agent: curl/7.79.1
0046: Accept: */*
0053: 
14:38:55.131822 == Info: Mark bundle as not supporting multiuse
14:38:55.131875 <= Recv header, 27 bytes (0x1b)
0000: HTTP/1.1 401 UNAUTHORIZED
14:38:55.131907 <= Recv header, 37 bytes (0x25)
0000: Date: Sat, 03 Sep 2022 07:38:55 GMT
14:38:55.131932 <= Recv header, 25 bytes (0x19)
0000: Server: gunicorn/19.9.0
14:38:55.131958 <= Recv header, 44 bytes (0x2c)
0000: WWW-Authenticate: Basic realm="Fake Realm"
14:38:55.131983 <= Recv header, 32 bytes (0x20)
0000: Access-Control-Allow-Origin: *
14:38:55.132004 <= Recv header, 40 bytes (0x28)
0000: Access-Control-Allow-Credentials: true
14:38:55.132028 <= Recv header, 33 bytes (0x21)
0000: Cache-Control: proxy-revalidate
14:38:55.132050 <= Recv header, 19 bytes (0x13)
0000: Content-Length: 0
14:38:55.132070 <= Recv header, 24 bytes (0x18)
0000: Connection: Keep-Alive
14:38:55.132091 <= Recv header, 2 bytes (0x2)
0000: 
14:38:55.132122 == Info: Connection #0 to host httpbin.org left intact
```

This can be used with `--trace`, `--trace-ascii` and `--verbose`.

Dictionary lookups with DICT protocol
-------------------------------------

DICT ([RFC 2229](https://www.rfc-editor.org/rfc/rfc2229)) is a application
level protocol for performing dictionary lookups. It can be used
via curl like this:

```
$ curl dict://dict.org/d:linux       
220 dict.dict.org dictd 1.12.1/rf on Linux 4.19.0-10-amd64 <auth.mime> <138373555.5356.1662191318@dict.dict.org>
250 ok
150 1 definitions retrieved
151 "linux" wn "WordNet (r) 3.0 (2006)"
Linux
    n 1: an open-source version of the UNIX operating system
.
250 ok [d/m/c = 1/0/30; 0.000r 0.000u 0.000s]
221 bye [d/m/c = 0/0/0; 0.000r 0.000u 0.000s]
```

This may seem like it's nothing to write home about. After all, we can
search Google with `define:` and the word we want to lookup. Scraping
Google SERPs either directly or through some SaaS API is not hard. However
this provides an example of a fairly obscure network protocol that
curl has support for.

Transferring files via (S)FTP
-----------------------------

Let us something bit more useful now. Curl can be used to transfer files
via FTP, SFTP and FTPS protocols. For example, we can use curl to list 
files on FTP server and download them:

```
$ curl --list-only ftp://ftp.sunet.se             
HEADER.html
Public
about
cdimage
conspiracy
debian
debian-cd
favicon.ico
images
mirror
pub
releases
robots.txt
tails
ubuntu
$ curl --list-only ftp://ftp.sunet.se/debian/
README
README.CD-manufacture
README.html
README.mirrors.html
README.mirrors.txt
dists
doc
extrafiles
indices
ls-lR.gz
pool
project
tools
zzz-dists
$ curl ftp://ftp.sunet.se/debian/README -o README
```

If we wanted to upload a local file to remote path at FTP server we could use 
`-T` or `--upload-file`. 

However plain text anonymous servers are going out of fashion within last couple 
decades. When we have SSH access to a remote server
we can also use SFTP - a more modern file transfer protocol that is built upon
the foundation of SSH. This is not merely FTP over SSH, but a separate protocol
designed from ground up by IETF. It is also more generalised than the legacy
SCP protocol. 

To use SFTP with curl, we would use the same URL format, except we would have
`sftp://` at the beginning. If username/password auth is required we can
pass the credentials in colon-separated form via `--user` option.

If we are trying to connect to FTPS (FTP over TLS) server we would use `ftps://`
for the URLs.

Sending and receiving email
---------------------------

Curl also supports SMTP protocol for email sending. Let us try sending an email
via Sendgrid. First we need to prepare a text file with some email headers and 
content. This is what we save into email.txt:

```
From: No Reply <noreply@keyspace.lt>
To: Test User <test2048@mailinator.com>
Subject: Test email

A specter is haunting the modern world, the specter of crypto anarchy.
```

A command to send this email is the following:

```
$ curl --insecure --ssl smtp://smtp.sendgrid.com:587 --user "apikey:[REDACTED]" --mail-rcpt "test2048@mailinator.com" --mail-from "noreply@keyspace.lt" --upload-file email.txt  
```

The redacted part is Sendgrind API key that we use as SMTP password. 

Curl can be used to send emails, but what about receiving them? This is also
possible via POP3 and IMAP protocols.

Let us first list message IDs and sizes via POP3 protocol:

```
$ curl pop3://pop3.rambler.ru --user "ermakova_g01bm@rambler.ru:[REDACTED]"
1 4388
```

We have a single message with ID 1 and size 4388. It can be downloaded by 
using the message ID as URL path:

```
$ curl pop3://pop3.rambler.ru/1 --user "ermakova_g01bm@rambler.ru:[REDACTED]" 
```

Things are a bit different with IMAP, as IMAP protocol supports different 
mailboxes that we can list:

```
$ curl --ssl imap://imap.rambler.ru/ --user "ermakova_g01bm@rambler.ru:[REDACTED]"    
* LIST (\HasNoChildren \UnMarked \Sent) "/" SentBox
* LIST (\HasNoChildren \Junk) "/" Spam
* LIST (\HasNoChildren \Marked \Trash) "/" Trash
* LIST (\HasNoChildren \Drafts) "/" DraftBox
* LIST (\HasNoChildren) "/" INBOX
```

To check the status of mailbox, let us send `examine` IMAP command:

```
$ curl --ssl "imap://mail.rambler.ru/" -X "examine INBOX" --user "ermakova_g01bm@rambler.ru:[REDACTED]" 
* FLAGS (\Answered \Flagged \Deleted \Seen \Draft)
* OK [PERMANENTFLAGS ()] Read-only mailbox.
* 2 EXISTS
* 0 RECENT
* OK [UIDVALIDITY 1644072147] UIDs valid
* OK [UIDNEXT 20] Predicted next UID
* OK [HIGHESTMODSEQ 37] Highest
```

To get a single message at specific index, query it like this:

```
$ curl --ssl "imap://mail.rambler.ru/INBOX;MAILINDEX=1" --user "ermakova_g01bm@rambler.ru:[REDACTED]"  
```

libcurl and it's bindings
-------------------------

Curl is not only a CLI tool, but also a C library with bindings available in a number of 
programming languages. If we have a curl snippet we can add `--libcurl` with file path
to generate some boilerplate C code:

```
$ curl http://httpbin.org/status/401 --libcurl example.c
```

It will generate something like this:

```c
/********* Sample code generated by the curl command line tool **********
 * All curl_easy_setopt() options are documented at:
 * https://curl.se/libcurl/c/curl_easy_setopt.html
 ************************************************************************/
#include <curl/curl.h>

int main(int argc, char *argv[])
{
  CURLcode ret;
  CURL *hnd;

  hnd = curl_easy_init();
  curl_easy_setopt(hnd, CURLOPT_BUFFERSIZE, 102400L);
  curl_easy_setopt(hnd, CURLOPT_URL, "http://httpbin.org/status/401");
  curl_easy_setopt(hnd, CURLOPT_NOPROGRESS, 1L);
  curl_easy_setopt(hnd, CURLOPT_USERAGENT, "curl/7.85.0");
  curl_easy_setopt(hnd, CURLOPT_MAXREDIRS, 50L);
  curl_easy_setopt(hnd, CURLOPT_HTTP_VERSION, (long)CURL_HTTP_VERSION_2TLS);
  curl_easy_setopt(hnd, CURLOPT_FTP_SKIP_PASV_IP, 1L);
  curl_easy_setopt(hnd, CURLOPT_TCP_KEEPALIVE, 1L);

  /* Here is a list of options the curl code used that cannot get generated
     as source easily. You may choose to either not use them or implement
     them yourself.

  CURLOPT_WRITEDATA set to a objectpointer
  CURLOPT_INTERLEAVEDATA set to a objectpointer
  CURLOPT_WRITEFUNCTION set to a functionpointer
  CURLOPT_READDATA set to a objectpointer
  CURLOPT_READFUNCTION set to a functionpointer
  CURLOPT_SEEKDATA set to a objectpointer
  CURLOPT_SEEKFUNCTION set to a functionpointer
  CURLOPT_ERRORBUFFER set to a objectpointer
  CURLOPT_STDERR set to a objectpointer
  CURLOPT_HEADERFUNCTION set to a functionpointer
  CURLOPT_HEADERDATA set to a objectpointer

  */

  ret = curl_easy_perform(hnd);

  curl_easy_cleanup(hnd);
  hnd = NULL;

  return (int)ret;
}
/**** End of sample code ****/
```

If you are not working in fairly deep systems programming you may not be willing
to code in C. However, there's libcurl bindings available in a lot of languages:

* C++ - [curlpp](http://www.curlpp.org/)
* Go - [go-curl](https://github.com/andelf/go-curl)
* Haskell - [curl Haskell package](https://hackage.haskell.org/package/curl)
* Java - [curl-java](https://github.com/pjlegato/curl-java)
* JavaScript - [node-libcurl](https://github.com/JCMais/node-libcurl)
* PHP - [PHP curl library](https://www.php.net/curl)
* Python - [PyCURL](http://pycurl.io/)
* Rust - [curl-rust](https://github.com/alexcrichton/curl-rust)

If you merely need to do some basic HTTP requests using libcurl is likely to be
an overkill. For example, Python requests module is far easier to use than 
PyCURL. However, if you're doing some nonstandard stuff libcurl might be a
good abstraction layer to base your code upon. For example, once I had to
integrate proxy servers that require TLS handshake to be performed
*before* HTTP CONNECT message is sent by the client. Using such proxy servers
is possible with PyCURL.
