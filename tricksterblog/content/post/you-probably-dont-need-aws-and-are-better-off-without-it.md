+++
author = "rl1987"
title = "You probably don't need AWS and are better off without it"
date = "2022-04-22"
draft = true
tags = ["devops"]
+++

Amazon Web Services (AWS) is the most prominent large cloud provider in the world, offering what seems to
be practically unlimited scalability and flexibility. It is heavily marketed towards startups and big companies
alike. There's even a version of AWS meant for extra-secure governmental use (AWS for Government). There's an
entire branch of DevOps industry that helps setting up software systems on AWS and a lot of people are
making money by using AWS in some capacity. AWS isn't just a VPS provider or web hosting service - 
there's entire periodic table of things they offer, ranging from commodity stuff such as virtual private
servers (EC2) or data storage (S3) to cutting edge experimental technologies such as quantum computation
(Amazon Braket) and artificial intelligence (SageMaker, Rekognition). It is simply too significant to be ignored.

However, is it actually that great? Is it actually good as default choice to host a software system of any scale?
Let us go through some arguments against going all-in with AWS and why many companies and individual side-project
developers might be better off using something else.

Pricing complexity and billing surprises
----------------------------------------

If you read AWS discussions on Hacker News or other developer communities you will find that the issue of billing
keeps popping up. AWS billing is a lot like taxes in USA - it depends on so many things and you can never be sure
how much you will be paying when the month is over. Furthermore, AWS billing is uncapped, which has significant
potential for trouble.

If you are using something that is billed based on traffic or resource usage (Lambda, Step Functions) you may have 
a very bad surprise in otherwise good situation of your project getting viral traction. Imagine a sudden wave of 
new users becoming the very reason of SaaS startup going bankrupt.

There are also ways to mess up your AWS Lambda "serverless" functions in ways that can rack up huge bills. Certain
bugs in code, such as infinite loop or bottomless recursion can make you go broke in a single monday morning.

Another way to get a billing surprise is to provision some resources and forget to take them down. A HN user
[reports](https://news.ycombinator.com/item?id=22719573) a story of someone who burning 80 grand overnight
by provisioning bunch of EC2 instances for testing and leaving them on. If you have non-trivial setup on AWS
(e.g. VPC with multiple EC2 instances, some of which exposed to public internet) and are relying on AWS 
Dashboard or AWS CLI to tear it down when no longer needed it is very easy to forget to remove some part
of it (e.g. NAT gateway) and be billed for it even if it's no longer used.

Yet another way to lose a lot of money is to get your AWS credentials stolen by bad people that will
use your account for their own purposes, such as cryptocurrency mining. There's multiple ways this can
happen. Someone might exploit a vulnerability in your app to access source code or configuration file
with AWS secrets. If you publish your code on public Github repo you might accidentally leak it yourself.

Now you could say that the above things are accidents, not unlike a car crash or fire in the office.
However, AWS pricing is significantly complex for specialist AWS cost optimisation consultants to
exist in the market. Depending on how exactly you are using the AWS infra, you may be be overpaying
significantly for what you are getting, especially if you consider options to host your systems
outside AWS.

One might say that it is possible to use CloudWatch alerts to fire on billing thresholds and get alerted.
However, the problem is that billing data is updated *after* resources are consumed and it might be too
late at that point. In fact, AWS has no reliable way to shut down your systems in the event of runaway 
costs.

Also one may respond that at least in some cases you can contact AWS support and have them write off
the surprise charges, even if they occured entirely due to your own mistake. That is indeed true to
my own experience. I was able to get $100+ written off when I forgot to remove a Private CA after
being done with it. Some people report being able not to pay multiple thousands of dollars in surprise
charges. However, this is entirely dependent on the goodwill of a very large corporation that is 
not known to treat their employees well and there might an explicit limit on how many times you can 
ask for it. It is not something to rely on.

You might be saying that AWS is actually free up to a point due to the presence of free tier,
free trials for some services and generous credits being given out to startups. But here's the thing - 
AWS is not providing free services out of goodness of their hearts. AWS giving out some tens of 
thousands of free credits to every single startup in certain accelerators is not unlike to a drug
dealer giving out free hits in a community susceptible to drug abuse. It is done in a calculated
manner so that customer life time value is very worthwhile on average case, even if some services
are provided for free initially. By taking up the free AWS offer you might be saving money short
term only to overpay in long term.

Vendor lock-in
--------------

AWS provides a seeming flexibility to develop cloud-native software. However, if you rely on AWS
APIs and services too much (for example by implementing a bulk of your codebase in Lambda functions)
AWS will become a hard, critical dependency to your systems. Problems with AWS infra can quickly
spread to your side. This was particularly evident during the recent years that disrupted
significant portions of the web. You will not be able to address these problems quickly if you
rely on AWS to work properly all the time (which it does not), unless you have a multi-cloud
setup that is deliberately designed to be resilient. Furthermore, AWS may decide that they hate
your app/company/project for whatever reason and cut you off, even if it is based on a false
positive in their anti-fraud analytics. If your code is written in such way
that it works on AWS or not at all this can be fatal to the project.

This can be largely avoided by limiting the code and infra dependencies to things that can be
replaced with acceptable cost, such as basic EC2 instances with mainstream Linux distributions
and open source equivalents to AWS stuff e.g. Terraform instead of CloudFormation, 
MinIO instead of S3 and so on. The flipside of this approach is that by avoiding AWS-specific services
and tools we maybe also be not getting the maximum value from AWS. For example, if all you use
are vanilla servers with Debian Linux you don't truly need AWS - there are simpler and
cheaper ways to set them up.

Devops complexity
-----------------



WRITEME: devops complexity

WRITEME: alternatives to AWS
