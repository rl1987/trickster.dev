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

WRITEME: IMAP explanation and email receiving flow

POP3: Post Office Protocol version 3
------------------------------------

WRITEME: POP3 explanation and email receiving flow

MIME: Multipurpose Internet Mail Extension
------------------------------------------

WRITEME: MIME explanation and some message examples

