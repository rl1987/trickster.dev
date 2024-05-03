+++
author = "rl1987"
title = "Simple ways to find exposed sensitive information"
date = "2024-05-31"
draft = true
tags = ["scraping", "osint", "security"]
+++

Sensitive Data Exposure is a type of vulnerability where software system (or 
user) makes sensitive data (API keys, user information, private documents, etc.) 
available to potential adversaries. For example, web app that lets users edit 
potentially confidential documents may be storing them in S3 buckets without
any proper access controls. This results in information that should not be
public being potentially available to those who know how to look for it. In this
post we will go through some basic techniques of Sensitive Data Discovery - 
the activity of hunting for accidental leaks of things that are best kept hidden.


WRITEME
