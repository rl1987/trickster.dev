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

WRITEME: SMTP explanation and sending flow

IMAP: Internet Message Access Protocol
--------------------------------------

WRITEME: IMAP explanation and email receiving flow

POP3: Post Office Protocol version 3
------------------------------------

WRITEME: POP3 explanation and email receiving flow

MIME: Multipurpose Internet Mail Extension
------------------------------------------

WRITEME: MIME explanation and some message examples

