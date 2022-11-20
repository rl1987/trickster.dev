+++
author = "rl1987"
title = "SMTP, IMAP, POP3 and MIME: understanding email protocols"
date = "2022-11-19"
draft = true
tags = ["networking"]
+++

Introduction and big picture
----------------------------

Email is a fairly old school technology meant to replicate postal service digitally.
To understand how email works, we must know about network protocols that specify sets 
of data formats and data exchange rules for exchanging messages over the network.
In the modern internet email sending part is conceptually (and sometimes technically)
separate from receiving part. Email sending aspects are formalised in RFCs that describe
SMTP protocol, whereas reception part can be done either via IMAP or POP3 protocol.
Furthermore, MIME data format is used for encoding contents and inner structure of the
messages that are transferred.

Broadly speaking, email system is federated and consists of the following parts:
* Mail Transfer Agent (MTA) is a program that implements SMTP protocol to transport messages
between hosts (e.g. Sendmail, qmail, Postfix).
* Mail User Agent (MUA) is the email client application (e.g. mutt, Mail.app, Outlook, 
Thunderbird).
* There can also be a Mail Delivery Agent (MDA) - an intermediate piece of software that
bridges the gap between MTA and MUA on the receiving side (e.g. procmail). 
This can be done for spam filtering purposes and to manage the email message 
persistence on Unix/Linux systems.
* Lastly, there can also be a Mail Submission Agent (MSA) that is equivalent of MDA, but
for sending the email.

The general big-picture flow of email message is the following:

1. A sender creates the email message and sends it from MUA to MTA managed by their email 
provider (possibly via MSA). SMTP protocol is being used here.
2. Message traverses one or more MTAs. Again, this is done via SMTP protocol.
3. Message reaches the final MTA belonging to the email provider of the recipient and is 
stored there.
4. Recipient uses MUA on their end to retrieve the message. Either IMAP or POP3 protocol
can be used here.

It should be noted that email provider specific REST API can be used between MUA and MTA
(possibly through a client library). For examples of such APIs, see:

* [Gmail API](https://developers.google.com/gmail/api)
* [ZOHO Mail API](https://www.zoho.com/mail/help/api/)
* [Sendgrid API](https://docs.sendgrid.com/api-reference/how-to-use-the-sendgrid-v3-api/authentication)

This would replace SMTP, IMAP and POP3 protocols for communications between client and server.

SMTP: Simple Mail Transfer Protocol
-----------------------------------

SMTP was originally formalised back in 1981 in [RFC 788](https://datatracker.ietf.org/doc/html/rfc788).
Since then, the protocol specification has been extended across various RFCs to keep
it up to data with the changing needs of growing internet. At the time of writing, 
[RFC 5321](https://datatracker.ietf.org/doc/html/rfc5321) is the final version of core
SMTP spec. SMTP is a text-based protocol with two kinds of messages: commands and
responses. 

Let us use `smtplib` module from the vanilla Python installation to explore the SMTP 
debugging output. We want to see the protocol flow.

```
$ python3
Python 3.10.8 (main, Oct 13 2022, 09:48:40) [Clang 14.0.0 (clang-1400.0.29.102)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import smtplib
>>> smtp_conn = smtplib.SMTP("smtp.rambler.ru", port=587)
>>> smtp_conn.set_debuglevel(1)
>>> smtp_conn.starttls()
send: 'ehlo [[REDACTED]]\r\n'
reply: b'250-mail.rambler.ru\r\n'
reply: b'250-SIZE 104857600\r\n'
reply: b'250-ENHANCEDSTATUSCODES\r\n'
reply: b'250-8BITMIME\r\n'
reply: b'250-AUTH PLAIN LOGIN\r\n'
reply: b'250 STARTTLS\r\n'
reply: retcode (250); Msg: b'mail.rambler.ru\nSIZE 104857600\nENHANCEDSTATUSCODES\n8BITMIME\nAUTH PLAIN LOGIN\nSTARTTLS'
send: 'STARTTLS\r\n'
reply: b'220 2.0.0 Start TLS\r\n'
reply: retcode (220); Msg: b'2.0.0 Start TLS'
(220, b'2.0.0 Start TLS')
```

We established TCP connection to SMTP server and sent `EHLO` command with our 
IP address to initiate the conversation. The server responded with status code
250 (indicating success) and a list of SMTP service extensions that server is supporting.
To make the connection encrypted, we also issued a `STARTTLS` command. To this command
server replied with status code 220, which means that it ready to serve the client.

Now we need to login to the server with account credentials. 

```
>>> username = "[REDACTED]"
>>> password = "[REDACTED]"
>>> smtp_conn.login(username, password)
send: 'ehlo [202.3.218.138]\r\n'
reply: b'250-mail.rambler.ru\r\n'
reply: b'250-SIZE 104857600\r\n'
reply: b'250-ENHANCEDSTATUSCODES\r\n'
reply: b'250-8BITMIME\r\n'
reply: b'250 AUTH PLAIN LOGIN\r\n'
reply: retcode (250); Msg: b'mail.rambler.ru\nSIZE 104857600\nENHANCEDSTATUSCODES\n8BITMIME\nAUTH PLAIN LOGIN'
send: 'AUTH PLAIN [REDACTED]\r\n'
reply: b'235 2.0.0 OK\r\n'
reply: retcode (235); Msg: b'2.0.0 OK'
(235, b'2.0.0 OK')
```

Calling `login()` method repeated the `EHLO` message over the now-encrypted channel
and sent `AUTH` message that deals with "PLAIN Simple Authentication and Security Layer 
(SASL) Mechanism" described in [RFC 4616](https://www.ietf.org/rfc/rfc4616.txt). The
redacted part is Base64 string from the following sequence:

* Null byte (0x00).
* Email account username.
* Null byte.
* Email account password.

We got response from the server saying that all is good with the login step. Now we 
can send some test message.

```
>>> to_addr = "noreply@keyspace.lt"
>>> smtp_conn.sendmail(username, to_addr, "Test!")
send: 'mail FROM:<[REDACTED]> size=5\r\n'
reply: b'250 2.1.0 Ok\r\n'
reply: retcode (250); Msg: b'2.1.0 Ok'
send: 'rcpt TO:<noreply@keyspace.lt>\r\n'
reply: b'250 2.1.5 Ok\r\n'
reply: retcode (250); Msg: b'2.1.5 Ok'
send: 'data\r\n'
reply: b'354 End data with <CR><LF>.<CR><LF>\r\n'
reply: retcode (354); Msg: b'End data with <CR><LF>.<CR><LF>'
data: (354, b'End data with <CR><LF>.<CR><LF>')
send: b'Test!\r\n.\r\n'
reply: b'250 2.0.0 Ok: queued as CB14F2642E52\r\n'
reply: retcode (250); Msg: b'2.0.0 Ok: queued as CB14F2642E52'
data: (250, b'2.0.0 Ok: queued as CB14F2642E52')
{}
```

There a sequence of three steps here:

1. We provide the email address of the sender which will correspond to email account
username in most cases via `MAIL FROM` command.
2. We provide recipient address via `RCPT TO` command. 
3. We send `DATA` command, contents of the message and message end sequence. In this
case the message is a very simple ASCII string, but in real world this is typically
a MIME payload that will be discussed later.

All step succeeded and a message was enqueued for further transfer. To finalise the 
connection in a clean way we would send a `QUIT` command.

We only covered the happy path here. [RFC 5321 Appendix D](https://datatracker.ietf.org/doc/html/rfc5321#appendix-D)
lists more examples.

Futhermore, modern SMTP implementation deal with additional considerations, such
as spam filtering and policy enforcement.

Standard TCP port of plaintext SMTP is 25. SMTP-over-TLS typically uses port 587.

One might ask: given an email address, how does MTA know the IP address of the next
MTA to pass the message to? This is typically found through DNS MX records that
point to hostname of the mail server servicing the given domain name.

IMAP: Internet Message Access Protocol
--------------------------------------

IMAPv4rev2 is the current version of IMAP protocol, specified in [RFC 9501](https://datatracker.ietf.org/doc/html/rfc9051).
This is fairly new standard that is not always implemented to the letter. However,
IMAP protocol has been around for long time and is widely supported in the world
of network software.

Let us receive an email with `imaplib` Python module and go through IMAP protocol flow.
We will enable debug output in Python REPL and reproduce the steps that email client
would do when receiving messages.

Like with SMTP protocol, we first need to establish the connection and login to an 
account.

```
>>> import imaplib
>>> imap_conn = imaplib.IMAP4_SSL("imap.rambler.ru", port=993)
>>> imap_conn.debug = 5
>>> imap_conn.login(username, password)
  33:33.96 > b'OGCE1 LOGIN [REDACTED] "[REDACTED]"'
  33:34.54 < b'OGCE1 OK [CAPABILITY IMAP4rev1 SASL-IR LOGIN-REFERRALS ID ENABLE IDLE SORT SORT=DISPLAY THREAD=REFERENCES THREAD=REFS THREAD=ORDEREDSUBJECT MULTIAPPEND URL-PARTIAL CATENATE UNSELECT CHILDREN NAMESPACE UIDPLUS LIST-EXTENDED I18NLEVEL=1 CONDSTORE QRESYNC ESEARCH ESORT SEARCHRES WITHIN CONTEXT=SEARCH LIST-STATUS BINARY MOVE SNIPPET=FUZZY PREVIEW=FUZZY PREVIEW STATUS=SIZE SAVEDATE LITERAL+ NOTIFY SPECIAL-USE QUOTA] Logged in'
  33:34.54 	matched b'(?P<tag>OGCE\\d+) (?P<type>[A-Z]+) (?P<data>.*)' => (b'OGCE1', b'OK', b'[CAPABILITY IMAP4rev1 SASL-IR LOGIN-REFERRALS ID ENABLE IDLE SORT SORT=DISPLAY THREAD=REFERENCES THREAD=REFS THREAD=ORDEREDSUBJECT MULTIAPPEND URL-PARTIAL CATENATE UNSELECT CHILDREN NAMESPACE UIDPLUS LIST-EXTENDED I18NLEVEL=1 CONDSTORE QRESYNC ESEARCH ESORT SEARCHRES WITHIN CONTEXT=SEARCH LIST-STATUS BINARY MOVE SNIPPET=FUZZY PREVIEW=FUZZY PREVIEW STATUS=SIZE SAVEDATE LITERAL+ NOTIFY SPECIAL-USE QUOTA] Logged in')
  33:34.54 	matched b'\\[(?P<type>[A-Z-]+)( (?P<data>.*))?\\]' => (b'CAPABILITY', b' IMAP4rev1 SASL-IR LOGIN-REFERRALS ID ENABLE IDLE SORT SORT=DISPLAY THREAD=REFERENCES THREAD=REFS THREAD=ORDEREDSUBJECT MULTIAPPEND URL-PARTIAL CATENATE UNSELECT CHILDREN NAMESPACE UIDPLUS LIST-EXTENDED I18NLEVEL=1 CONDSTORE QRESYNC ESEARCH ESORT SEARCHRES WITHIN CONTEXT=SEARCH LIST-STATUS BINARY MOVE SNIPPET=FUZZY PREVIEW=FUZZY PREVIEW STATUS=SIZE SAVEDATE LITERAL+ NOTIFY SPECIAL-USE QUOTA', b'IMAP4rev1 SASL-IR LOGIN-REFERRALS ID ENABLE IDLE SORT SORT=DISPLAY THREAD=REFERENCES THREAD=REFS THREAD=ORDEREDSUBJECT MULTIAPPEND URL-PARTIAL CATENATE UNSELECT CHILDREN NAMESPACE UIDPLUS LIST-EXTENDED I18NLEVEL=1 CONDSTORE QRESYNC ESEARCH ESORT SEARCHRES WITHIN CONTEXT=SEARCH LIST-STATUS BINARY MOVE SNIPPET=FUZZY PREVIEW=FUZZY PREVIEW STATUS=SIZE SAVEDATE LITERAL+ NOTIFY SPECIAL-USE QUOTA')
  33:34.54 untagged_responses[CAPABILITY] 0 += ["b'IMAP4rev1 SASL-IR LOGIN-REFERRALS ID ENABLE IDLE SORT SORT=DISPLAY THREAD=REFERENCES THREAD=REFS THREAD=ORDEREDSUBJECT MULTIAPPEND URL-PARTIAL CATENATE UNSELECT CHILDREN NAMESPACE UIDPLUS LIST-EXTENDED I18NLEVEL=1 CONDSTORE QRESYNC ESEARCH ESORT SEARCHRES WITHIN CONTEXT=SEARCH LIST-STATUS BINARY MOVE SNIPPET=FUZZY PREVIEW=FUZZY PREVIEW STATUS=SIZE SAVEDATE LITERAL+ NOTIFY SPECIAL-USE QUOTA'"]
('OK', [b'[CAPABILITY IMAP4rev1 SASL-IR LOGIN-REFERRALS ID ENABLE IDLE SORT SORT=DISPLAY THREAD=REFERENCES THREAD=REFS THREAD=ORDEREDSUBJECT MULTIAPPEND URL-PARTIAL CATENATE UNSELECT CHILDREN NAMESPACE UIDPLUS LIST-EXTENDED I18NLEVEL=1 CONDSTORE QRESYNC ESEARCH ESORT SEARCHRES WITHIN CONTEXT=SEARCH LIST-STATUS BINARY MOVE SNIPPET=FUZZY PREVIEW=FUZZY PREVIEW STATUS=SIZE SAVEDATE LITERAL+ NOTIFY SPECIAL-USE QUOTA] Logged in'])
```

Unlike with SMTP connection, we establish TLS connection to server first and start 
sending IMAP commands in the encrypted channel. IMAP protocol does not have any 
equivalent of `STARTTLS` message to upgrade plaintext connection to an encrypted one.

`LOGIN` command was sent with username and password. Server responded with status `OK` and
a list of supported capabilities.

Now we need to select a mailbox on the server. If we provide no mailbox name the Python IMAP
client will switch to inbox by default.

```
>>> imap_conn.select()
  34:03.21 > b'OGCE2 SELECT INBOX'
  34:03.72 < b'* FLAGS (\\Answered \\Flagged \\Deleted \\Seen \\Draft)'
  34:03.72 	matched b'\\* (?P<type>[A-Z-]+)( (?P<data>.*))?' => (b'FLAGS', b' (\\Answered \\Flagged \\Deleted \\Seen \\Draft)', b'(\\Answered \\Flagged \\Deleted \\Seen \\Draft)')
  34:03.72 untagged_responses[FLAGS] 0 += ["b'(\\Answered \\Flagged \\Deleted \\Seen \\Draft)'"]
  34:03.72 < b'* OK [PERMANENTFLAGS (\\Answered \\Flagged \\Deleted \\Seen \\Draft \\*)] Flags permitted.'
  34:03.72 	matched b'\\* (?P<type>[A-Z-]+)( (?P<data>.*))?' => (b'OK', b' [PERMANENTFLAGS (\\Answered \\Flagged \\Deleted \\Seen \\Draft \\*)] Flags permitted.', b'[PERMANENTFLAGS (\\Answered \\Flagged \\Deleted \\Seen \\Draft \\*)] Flags permitted.')
  34:03.72 untagged_responses[OK] 0 += ["b'[PERMANENTFLAGS (\\Answered \\Flagged \\Deleted \\Seen \\Draft \\*)] Flags permitted.'"]
  34:03.72 	matched b'\\[(?P<type>[A-Z-]+)( (?P<data>.*))?\\]' => (b'PERMANENTFLAGS', b' (\\Answered \\Flagged \\Deleted \\Seen \\Draft \\*)', b'(\\Answered \\Flagged \\Deleted \\Seen \\Draft \\*)')
  34:03.72 untagged_responses[PERMANENTFLAGS] 0 += ["b'(\\Answered \\Flagged \\Deleted \\Seen \\Draft \\*)'"]
  34:03.72 < b'* 10 EXISTS'
  34:03.72 	matched b'\\* (?P<data>\\d+) (?P<type>[A-Z-]+)( (?P<data2>.*))?' => (b'10', b'EXISTS', None, None)
  34:03.72 untagged_responses[EXISTS] 0 += ["b'10'"]
  34:03.72 < b'* 4 RECENT'
  34:03.72 	matched b'\\* (?P<data>\\d+) (?P<type>[A-Z-]+)( (?P<data2>.*))?' => (b'4', b'RECENT', None, None)
  34:03.72 untagged_responses[RECENT] 0 += ["b'4'"]
  34:03.72 < b'* OK [UNSEEN 7] First unseen.'
  34:03.72 	matched b'\\* (?P<type>[A-Z-]+)( (?P<data>.*))?' => (b'OK', b' [UNSEEN 7] First unseen.', b'[UNSEEN 7] First unseen.')
  34:03.72 untagged_responses[OK] 1 += ["b'[UNSEEN 7] First unseen.'"]
  34:03.72 	matched b'\\[(?P<type>[A-Z-]+)( (?P<data>.*))?\\]' => (b'UNSEEN', b' 7', b'7')
  34:03.72 untagged_responses[UNSEEN] 0 += ["b'7'"]
  34:03.72 < b'* OK [UIDVALIDITY 1644072125] UIDs valid'
  34:03.72 	matched b'\\* (?P<type>[A-Z-]+)( (?P<data>.*))?' => (b'OK', b' [UIDVALIDITY 1644072125] UIDs valid', b'[UIDVALIDITY 1644072125] UIDs valid')
  34:03.72 untagged_responses[OK] 2 += ["b'[UIDVALIDITY 1644072125] UIDs valid'"]
  34:03.72 	matched b'\\[(?P<type>[A-Z-]+)( (?P<data>.*))?\\]' => (b'UIDVALIDITY', b' 1644072125', b'1644072125')
  34:03.72 untagged_responses[UIDVALIDITY] 0 += ["b'1644072125'"]
  34:03.72 < b'* OK [UIDNEXT 11] Predicted next UID'
  34:03.72 	matched b'\\* (?P<type>[A-Z-]+)( (?P<data>.*))?' => (b'OK', b' [UIDNEXT 11] Predicted next UID', b'[UIDNEXT 11] Predicted next UID')
  34:03.72 untagged_responses[OK] 3 += ["b'[UIDNEXT 11] Predicted next UID'"]
  34:03.72 	matched b'\\[(?P<type>[A-Z-]+)( (?P<data>.*))?\\]' => (b'UIDNEXT', b' 11', b'11')
  34:03.72 untagged_responses[UIDNEXT] 0 += ["b'11'"]
  34:03.72 < b'* OK [HIGHESTMODSEQ 17] Highest'
  34:03.72 	matched b'\\* (?P<type>[A-Z-]+)( (?P<data>.*))?' => (b'OK', b' [HIGHESTMODSEQ 17] Highest', b'[HIGHESTMODSEQ 17] Highest')
  34:03.72 untagged_responses[OK] 4 += ["b'[HIGHESTMODSEQ 17] Highest'"]
  34:03.72 	matched b'\\[(?P<type>[A-Z-]+)( (?P<data>.*))?\\]' => (b'HIGHESTMODSEQ', b' 17', b'17')
  34:03.72 untagged_responses[HIGHESTMODSEQ] 0 += ["b'17'"]
  34:03.72 < b'OGCE2 OK [READ-WRITE] Select completed (0.009 + 0.000 + 0.008 secs).'
  34:03.72 	matched b'(?P<tag>OGCE\\d+) (?P<type>[A-Z]+) (?P<data>.*)' => (b'OGCE2', b'OK', b'[READ-WRITE] Select completed (0.009 + 0.000 + 0.008 secs).')
  34:03.72 	matched b'\\[(?P<type>[A-Z-]+)( (?P<data>.*))?\\]' => (b'READ-WRITE', None, None)
  34:03.72 untagged_responses[READ-WRITE] 0 += ["b''"]
('OK', [b'10'])
```

We got several lines in response that deal with message UIDs - 32-bit numbers that
uniquely identify messages within the email account.

* `UIDVALIDITY` ...

Now we can search within selected mailbox for messages matching some predicate
(e.g. sender address being equal to known value). For the purpose of this example,
we will retrieve a list of UIDs of all messages in the inbox.

```
>>> imap_conn.search(None, 'ALL')
  34:42.42 > b'OGCE3 SEARCH ALL'
  34:42.73 < b'* SEARCH 1 2 3 4 5 6 7 8 9 10'
  34:42.73 	matched b'\\* (?P<type>[A-Z-]+)( (?P<data>.*))?' => (b'SEARCH', b' 1 2 3 4 5 6 7 8 9 10', b'1 2 3 4 5 6 7 8 9 10')
  34:42.73 untagged_responses[SEARCH] 0 += ["b'1 2 3 4 5 6 7 8 9 10'"]
  34:42.73 < b'OGCE3 OK Search completed (0.001 + 0.000 secs).'
  34:42.73 	matched b'(?P<tag>OGCE\\d+) (?P<type>[A-Z]+) (?P<data>.*)' => (b'OGCE3', b'OK', b'Search completed (0.001 + 0.000 secs).')
  34:42.73 untagged_responses[SEARCH] => [b'1 2 3 4 5 6 7 8 9 10']
('OK', [b'1 2 3 4 5 6 7 8 9 10'])
```

We got a list of UIDs from 1 to 10. To get a single message, we can send a `FETCH` command (response
removed for the sake of brevity):

```
>>> imap_conn.fetch(b'10', '(RFC822)')
  35:08.76 > b'OGCE5 FETCH 10 (RFC822)'
  35:09.15 < b'* 10 FETCH (FLAGS (\\Seen \\Recent) RFC822 {2940}'
  35:09.15 	matched b'\\* (?P<data>\\d+) (?P<type>[A-Z-]+)( (?P<data2>.*))?' => (b'10', b'FETCH', b' (FLAGS (\\Seen \\Recent) RFC822 {2940}', b'(FLAGS (\\Seen \\Recent) RFC822 {2940}')
  35:09.15 	matched b'.*{(?P<size>\\d+)}$' => (b'2940',)
```

In the response we get a MIME payload with all the headers.

Finally, we close the connection and logout:

```
>>> imap_conn.close()
  36:17.68 > b'OGCE7 CLOSE'
  36:17.96 < b'OGCE7 OK Close completed (0.001 + 0.000 secs).'
  36:17.96 	matched b'(?P<tag>OGCE\\d+) (?P<type>[A-Z]+) (?P<data>.*)' => (b'OGCE7', b'OK', b'Close completed (0.001 + 0.000 secs).')
('OK', [b'Close completed (0.001 + 0.000 secs).'])
>>> imap_conn.logout()
  36:22.24 > b'OGCE8 LOGOUT'
  36:22.57 < b'* BYE Logging out'
  36:22.57 	matched b'\\* (?P<type>[A-Z-]+)( (?P<data>.*))?' => (b'BYE', b' Logging out', b'Logging out')
  36:22.57 untagged_responses[BYE] 0 += ["b'Logging out'"]
  36:22.57 BYE response: b'Logging out'
('BYE', [b'Logging out'])
```

POP3: Post Office Protocol version 3
------------------------------------

WRITEME: POP3 explanation and email receiving flow

MIME: Multipurpose Internet Mail Extension
------------------------------------------

WRITEME: MIME explanation and some message examples

