+++
author = "rl1987"
title = "Understanding SPF, DKIM, DMARC for email security and deliverability"
date = "2022-11-25"
draft = true
tags = ["automation", "python", "growth-hacking", "security", "bug-bounties"]
+++

On it's own SMTP protocol does not do much validation on the authenticity of sender.
One can spoof protocol headers at SMTP and MIME levels to send a message in another
users name. That can be problematic as it makes spam and social engineering attacks 
easier. To address this problem, some email authentication technologies have been
developed. We will discuss the three major ones: SPF, DKIM and DMARC. SPF and DKIM
authenticate sender metadata and DMARC extends them to configure email handling
in case authentication fails. All of these rely on DNS records for the sender domain.

SPF: Sender Policy Framework
----------------------------

Sender Policy Framework, specified in [RFC 7208](https://www.rfc-editor.org/rfc/rfc7208)
is a way for domain owners to authorize or disallow email sending from email addresses
associated with that domain via DNS TXT records. This sets a policy regarding what entities
(if any) can use the domain for their sender email identities. If a receiving or intermediate email
server is compliant with SPF, it would check the DNS records against source email address
in the SMTP `HELO`/`EHLO`/`MAIL FROM` messages and base the decision to allow or reject 
the message based on the policy that domain owner has published. If a sending domain does
not publish any SPF records, the SPF-compliant email server is allowed to drop the email
message, which has implications for email deliverability. Setting up SPF records is one
of the recommended practices to prepare a domain for sending cold email.

Suppose we have a domain example.org and we want to disallow any and all email from that
domain. We would publish the following DNS TXT record:

```
v=spf1 -all
```

All SPF records start with version prefix `v=spf1` and contains zero or more 
directives (mechanism-qualifier pairs). It can also contains some optional modifiers.

In this case `-` is a qualifier that means "fail" (i.e. hard error on sending) and `all` 
is a mechanism that matches all sender IP addresses.

On the other, if we wanted everyone to be allowed to use the domain for email sending,
we could publish this:

```
v=spf1 +all
```

Now there's a qualifier `+` that means "pass", thus email sending is allowed from all
IP addresses.

There are two more possible qualifiers. `~` means "softfail", which corresponds to lesser
error condition on sending an email. This may cause email to be marked as possible spam
or bounced with a note to retry it later. `?` neither allows not disallows email to be
sent.

There are the following mechanisms that SPF supports:

* `all` - match any and all sender IP addresses
* `include` - include SPF records from other domain (e.g. `include:example.net`)
* `a` - match all IPs in domain name A records (e.g. just `a` for the current domain or
`a:example.net` for another domain)
* `mx` - match all IPs in domain name MX records (can also point to another DNS name)
* `ptr` - match IP addresses that reversely-resolves to given domain name or its subdomain 
(not recommended)
* `ip4` - match a single IPv4 address or IPv4 range (e.g. `ip4:1.2.3.4` or `ip4:192.168.0.1/16`)
* `ip6` - like `ip4`, but for IPv6 addresses
* `exists` - takes a domain spec and matches iff that matches at least one A record; meant 
for advanced use cases.

SPF implementations go through directives from left to right until it finds the one
that conclusively (dis)allows email transfer, runs into error conditions or runs out
of directives to check. In the case of conflicting directives, the one earlier in the
records has precedence.

At the end of the SPF record there can be the following modifiers:

* `redirect` - redirect SPF policy checks to another domain
* `exp` - used for configuring error message when email is rejected.

Now that we're familiar with concepts and some technical details of SPF, let us see
how SPF is implemented by a real world email provider - hey.com. We use dig(1)
to see what kind of SPF records hey.com domain has published:

```
$ dig -t TXT hey.com | grep spf1
hey.com.		60	IN	TXT	"v=spf1 include:_spf.hey.com ~all"
```

There's two SPF directives here:

* `include:_spf.hey.com` - include SPF policy of subdomain
* `~all` - soft-reject all email that is not covered by any other directive.

The `include` mechanism triggers recursive check. Now we must check the SPF records
of a referenced subdomain:

```
$ dig -t TXT _spf.hey.com | grep spf1
_spf.hey.com.		120	IN	TXT	"v=spf1 ip4:204.62.114.0/23 -all"
```

This specifies an IPv4 address range that is allowed to send email messages
from mailboxes under hey.com domain and strongly forbids all email traffic
to be sent from elsewhere, thus overriding the `~all` directive in the previous
record.

If you are growth hacker working on cold emails campaigns it is strongly
recommended to set up SPF for all your outreach domains. Your email provider
will most likely provide the exact instructions on how to do that.

But what if you want to do bug bounties? In that case, SPF records or lack
thereof are not that relevant. Missing SPF records are not generally considered
to be a serious security problem and reporting that is unlikely to lead to any
payout.

DKIM: Domain Keys Identified Mail
---------------------------------

DKIM, specified in [RFC 6376](https://www.rfc-editor.org/rfc/rfc6376) and some
other additional RFCs goes beyond simple domain-level policies and enables 
email message signing by public key published in DNS record. This lets the
intermediate email server to check if email message was sent from the
keeper of respective private key (e.g. sender email provider) and that there 
was no tampering by adversarial parties (e.g. rogue email servers) as the 
message was enroute to the recipient. Depending on how exactly DKIM is deployed,
the cryptographic signature may cover all message or only some headers.

DKIM also relies on DNS TXT records, but they are required to be published
at subdomain of following form: `[selector]._domainkey.[domain]`. Here
`selector` is provider-specific value and `domain` is a sender domain.

The DKIM signature is computed by sending email server that is managed
by your email provider. As the email message goes through further 
DKIM-compliant servers it is being verified for the valid signature. 
DKIM implementation by itself does not reject any messages, but introduces 
extra email headers that can be used by spam filtering solutions. 

DKIM has implications for email deliverability. As far as anti-spam systems
are concerned, lack of DKIM record means less reliable sender identity.
Furthermore, DKIM misconfiguration can cause signature validation to fail,
which can lead to message being filtered as spam (especially if DMARC is 
being used).

RFC 6367 provides the following example of `DKIM-Signature` header:

```
DKIM-Signature: v=1; a=rsa-sha256; d=example.net; s=brisbane;
   c=simple; q=dns/txt; i=@eng.example.net;
   t=1117574938; x=1118006938;
   h=from:to:subject:date;
   z=From:foo@eng.example.net|To:joe@example.com|
    Subject:demo=20run|Date:July=205,=202005=203:44:08=20PM=20-0700;
bh=MTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTI=;
b=dzdVyOfAKCdLXdJOc9G2q8LoXSlEniSbav+yuU4zGeeruD00lszZVoG4ZHRNiYzR
```

The following is an example of DKIM record that ZOHO provides:

```
v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDXzlbk53i+yhhnbLM6Z/dzASCoGrRMbnMJzFsJK9Q17cHVDqmSUjQkNMfBhMD0JgwZcuUpHBE2aTVzwaLEQXRkR7BDOLBY+JpGjtJ45sjI9rmlN/4ntJLFEzuGaaHDp/XyR3eORKSt2QBHs9OM9U8zMoXCQc1+MW6vbtYJeWhacwIDAQAB
```

Like with SPF, your email provider will probably give you exact DNS
record to use for enabling DKIM for your domain.

DMARC: Domain-based Message Authentication, Reporting and Conformance
---------------------------------------------------------------------

WRITEME
