+++
author = "rl1987"
title = "Sending notifications programmatically: let me count the ways"
date = "2022-03-11"
draft = true
tags = ["automation", "python", "growth-hacking", "security", "bug-bounties"]
+++

You may want to get notified about certain events happening during your scraping/botting operations. Examples
might be an outages of external systems that your setup depends on, fatal error conditions, scraping jobs
being finished. If you are implementing automations for bug bounty hunting, you certaintly want to get notified
about new vulnerabilities being found in target systems being scanned. You may also want to get periodic status 
updates on long running tasks. This requires integrating one or more messaging channels into your code.

Sending emails
--------------

Let's start with least urgent kind of notification - a simple email message. SMTP (Simple Mail Transfer Protocol)
is a standard way to send email messages and is implemented in many programming languages. For example, vanilla
Python installation includes module called `smtplib` that can be used to send email messages. This requires an
email account with functional SMTP interface. It is supported by most email providers, altough you may need to adjust
your settings on some of them. Alternatively, you can use email sending SaaS vendor such as [SendGrid](https://sendgrid.com/)
or [AWS SES](https://aws.amazon.com/ses/).

A very basic example of using Python SMTP API is provided by the official documentation:

```python
import smtplib

def prompt(prompt):
    return input(prompt).strip()

fromaddr = prompt("From: ")
toaddrs  = prompt("To: ").split()
print("Enter message, end with ^D (Unix) or ^Z (Windows):")

# Add the From: and To: headers at the start!
msg = ("From: %s\r\nTo: %s\r\n\r\n"
       % (fromaddr, ", ".join(toaddrs)))
while True:
    try:
        line = input()
    except EOFError:
        break
    if not line:
        break
    msg = msg + line

print("Message length is", len(msg))

server = smtplib.SMTP('localhost')
server.set_debuglevel(1)
server.sendmail(fromaddr, toaddrs, msg)
server.quit()
```

This sample code assumes that you have a local SMTP server running and that you are not using TLS for your SMTP connections.
That will not always be the case. Let us try sending a simple email message via Sendgrid. Now we are connecting to non-standard
SMTP port, wrapping SMTP communications in the TLS connection for security purposes and using SMTP authentication with username
`apikey` and password being the API key we are getting from SendGrid dashboard. Even so, sending an email from Python REPL is
rather simple:

```
>>> import smtplib
>>> smtp = smtplib.SMTP("smtp.sendgrid.com", port=2525)
>>> smtp.starttls()
(220, b'Begin TLS negotiation now')
>>> smtp.login("apikey", "[REDACTED]")
(235, b'Authentication successful')
>>> from email.message import EmailMessage
>>> msg = EmailMessage()
>>> msg.set_content("Hello via SendGrid")
>>> msg['Subject'] = "Test"
>>> msg['From'] = "noreply@keyspace.lt"
>>> msg['To'] = "noreply@keyspace.lt"
>>> msg.as_string()
'Content-Type: text/plain; charset="utf-8"\nContent-Transfer-Encoding: 7bit\nMIME-Version: 1.0\nSubject: Test\nFrom: noreply@keyspace.lt\nTo: noreply@keyspace.lt\n\nHello via SendGrid\n'
>>> smtp.send_message(msg)
{}
>>> smtp.close()
```

Here we used `email` module to construct the exact textual structure of message we are sending, which is generally more desirable
over having your code generate it, like it was done in `smtplib` sample code.

Note however that you would need to go through a procedure of verifying your sender email address with SendGrid or AWS SES.

However it might be that you prefer using REST APIs for everything. SendGrid also supports sending email via 
[REST API](https://docs.sendgrid.com/api-reference/mail-send/mail-send) and even has some client libraries in multiple
languages, including Python.

[SendGrid Python module](https://github.com/sendgrid/sendgrid-python) enables us to send emails via API that largely abstracts
away network protocol details:

```
>>> import sendgrid
>>> from sendgrid.helpers.mail import *
>>> client = sendgrid.SendGridAPIClient("[REDACTED]") # <-- API key
>>> from_email = "noreply@keyspace.lt"
>>> to_email = "noreply@keyspace.lt"
>>> subject = "Test #2"
>>> content = Content(mime_type="text/plain", content="Hello via SendGrid API")
>>> mail = Mail(from_email, to_email, subject, content)
>>> resp = client.send(mail)
>>> resp
<python_http_client.client.Response object at 0x106a35eb0>
>>> resp.status_code
202
```

However this would introduce a vendor-specific library in our code base, which is not always desirable, as switching to another
vendor for sending emails would be harder than simply changing SMTP server settings.

It should be noted that GMail also has REST API with some client libraries that allow sending emails programmatically, but
requires implementing OAuth flow, which makes it somewhat harder to integrate into scraping/automation scripts.

Sending Telegram notifications
------------------------------

Perhaps you don't use email that much nowadays and reserve it for important communications, such as clueless recruiter or HR
person asking you if you have five years of experience in a technology that emerged one year ago. Or perhaps you need to be
notified in a way that enables more urgent response. This is where messenger notifications come into picture. Modern IM platforms
typically have mobile apps, which enables you to receive push notifications when you receive direct (private?) messages that your
code will be sending. One of these platforms is Telegram.

To register for API access with Telegram, you will need to contact `@BotFather` via direct message and answer some questions
regarding your bot. Once the registration procedure is finished, you will get an API key for Telegram HTTP API. You may 
have heard about [Telethon](https://docs.telethon.dev/en/stable/) - a Python module for building Telegram bots that largely
relies on asynchronuous programming techniques. Telethon is not needed for simply sending notifications, as REST API will
be enough.

To start receiving notifications, you would need to DM your bot with message `/start`. This will register you as having initiated
a conversation with the bot. Bots are not allowed to initiate chats with regular users.

To send a message, we have to get a list of chat IDs first:

```python
import requests


def find_chat_ids(token):
    chat_ids = set()

    url = "https://api.telegram.org/bot{}/getUpdates".format(token)

    resp = requests.get(url)

    json_dict = resp.json()

    results = json_dict.get("result", [])

    for rd in results:
        chat_id = rd.get("message", dict()).get("chat", dict()).get("id")
        chat_ids.add(chat_id)

    return list(chat_ids)
```

Once you have a list of chat IDs you can message all subscribers by posting chat ID and message contents to the API:

```python
    for chat_id in find_chat_ids(token):
        data = {"chat_id": chat_id, "text": message}

        url = "https://api.telegram.org/bot{}/sendMessage".format(token)

        resp = requests.post(url, data=data)
```

Sending Discord notifications
-----------------------------

Similarly to Telegram, Discord also provides an [API](https://discord.com/developers/docs/intro) for bot development that
requires you to register your bot at developer portal to get credentials for API access. 
[discord-py](https://discordpy.readthedocs.io/en/stable/) is a prominent Python module for implementing Discord chat bots, 
To send a DM programmatically you don't need a registration step from the user, but the user has to be present in the same 
"server"/guild as the bot. Alternatively, your bot could send chat messages to a regular channel on Discord.

A gray hat approach would be what's called "self-botting" - automating against private Discord API and pretending to be a
regular user when sending messages. However Discord is deploying countermeasures against things like that.

Sending SMS message via Twilio
------------------------------

Perhaps you don't want to rely on some IM platform to notify you and don't mind spending a bit of money to set up notifications
in a way that makes them reach you even if you don't have TCP/IP connectivity on your smartphone. This is where goold old
Short Message Service (SMS) comes in. To start sending SMS messages programmatically, we first need to sign up at
[Twilio](https://www.twilio.com/) - a prominent SaaS vendor that exposes telecommunications features via REST API for easy
integration. Then we would purchase a phone number and get an API credentials (account SID and auth token).

Now we have 3 ways to send an SMS message: 

* Calling REST API directly:

```
$ curl -X POST https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID/Messages.json \
--data-urlencode "Body=Hello there!" \
--data-urlencode "From=[REDACTED]" \
--data-urlencode "To=[REDACTED]" \
-u $TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN
```

* Using `twilio` Python module (or any of the other client libraries that Twilio provides):

```python
from twilio.rest import Client

account_sid = "[REDACTED]"
auth_token = "[REDACTED]"
client = Client(account_sid, auth_token)

message = client.messages.create( body="Hello there!", from_='[REDACTED]', to='[REDACTED]')
```

* Using [Twilio CLI](https://www.twilio.com/docs/twilio-cli/quickstart) tool:

```
$ twilio api:core:messages:create --from "[REDACTED]" --to "[REDACTED]" --body "Hello there!"
```

All phone numbers have to in E.164 format, e.g. "+14155552671".

Making a phone call via Twilio
------------------------------

Sometimes things are getting complicated and may require waking you or a support engineer in the middle of the night
to immediately address issues that have emerged. Thus we need to make a phone call, that we can also do via Twilio in all
3 ways that applies for sending SMS. However there is one key difference - when making a phone call via Twilio API
we have to pass a [TwiML](https://www.twilio.com/docs/voice/twiml) payload that will define interaction with the user
that picks up the phone. This can be a rather complex flow, but for the sake of simplicity let us make Twilio use 
text-to-speech synthesis to pass a message for us:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say>Data center is on fire!</Say>
</Response>
```

Let us make a phone call from Python REPL:

```
>>> from twilio.rest import Client
>>> client = Client("[REDACTED]", "[REDACTED]")
>>> call = client.calls.create(twiml='<Response><Say>Data center is on fire!</Say></Response>', to="[REDACTED]", from_="[REDACTED]")
```



