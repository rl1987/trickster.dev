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

WRITEME

DKIM: Domain Keys Identified Mail
---------------------------------

WRITEME

DMARC: Domain-based Message Authentication, Reporting and Conformance
---------------------------------------------------------------------

WRITEME
