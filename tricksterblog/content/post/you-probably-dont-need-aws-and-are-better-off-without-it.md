+++
author = "rl1987"
title = "You probably don't need AWS and are better off without it"
date = "2022-04-20"
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
[reports](https://news.ycombinator.com/item?id=22719573) a story of someone who burned 80 grand overnight
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
spread to your side. This was particularly evident during the outages in recent years that disrupted
significant portions of the web. You will not be able to address these problems quickly if you
rely on AWS to work properly all the time (which it does not), unless you have a multi-cloud
setup that is deliberately designed to be resilient. Furthermore, AWS may decide that they hate
your app/company/project for whatever reason and cut you off, even if it is based on a false
positive in their anti-fraud analytics. If your code is written in such way
that it works on AWS or not at all this can be fatal to the project.

This can be largely avoided by limiting the code and infra dependencies to things that can be
replaced with acceptable cost, such as basic EC2 instances with mainstream Linux distributions
and open source equivalents to AWS stuff e.g. PostgreSQL instead of DynamoDB,
MinIO instead of S3 and so on. The flipside of this approach is that by avoiding AWS-specific services
and tools we maybe also be not getting the maximum value from AWS. For example, if all you use
are vanilla servers with Debian Linux you don't truly need AWS - there are simpler and
cheaper ways to set them up.

Devops complexity
-----------------

Last but not least, there's devops complexity. Web interface of AWS is not exactly known for it's usability.
Developers and technical users would probably prefer AWS CLI. For things like automated CI/CD pipelines
we can use client libraries (such as boto3 for Python) or infrastructure-as-code tools such as Ansible,
Terraform, Puppet, Chef. This makes things easier in some ways as we only need to get the configuration
or script right once and we can benefit from it in the future without having to remember how to perform tedious manual
steps through a browser. However, using Python or Terraform for has its own challenges and may turn out
to be harder than it looks. 

For example, consider setting up a Kubernetes cluster on AWS. It used to be that we would need to use
solution like [kops](https://kubernetes.io/docs/setup/production-environment/tools/kops/) to do it, but
now AWS offers EKS - a managed Kubernetes service. So it should be fairly easy, right? Well, not so quick.
Setting up EKS cluster with actual compute is far from one-click (or one Unix command) process. Configuring
VPC for EKS cluster is harder than one expect it should be. We can do this through Terraform, as AWS
is officially supported through Terraform adapter. This cuts down the waste of effort, but when setting up
VPC for EKS cluster I had to make a compromise and use `aws_cloudformation_stack` resource to pull in
the example CloudFormation configuration and create VPC from that. This worked fairly well, but there was
a degree of impendance mismatch between Terraform stuff and CloudFormation stuff. This manifested during
infrastructure teardown - some networking resources (NAT gateways, subnets) could not always be cleaned up
due to what appeared to Terraform to be circular dependencies. Running `terraform destroy` would fail with
an error and I would be left with the task of fighting some errors through AWS console to make sure everything
is cleanly removed. After some fiddling, this was solved by using `depends_on` statements in Terraform configuration.

Digital Ocean also offers a managed Kubernetes service that you can set up within minutes by going through
a simple process consisting of few steps. It's not exactly one-click, but close to that. At the end, you
also end up with a functioning Kubernetes cluster, but there's far less hassle getting there. Compare
and contrast this with AWS EKS, which may easily eat up a day of your time, especially if you're not
upfront familiar with it. There's a tool called [eksctl](https://eksctl.io/) to make it easier, but
setting up EKS cluster is generally much harder than using DOKS.

People may be saying that a company using AWS is saving money as the alternative would be getting a server
that would not only incur capital expenses of buying the server hardware, but also operational expenses
to have a systems administrator employed so that the server would be properly managed. One may question
if that is true simply because using AWS at scale is not exactly cheap operationally. Furthermore,
chances are the company is not saving money on employees as managing stuff on AWS is not easy; it's just
that the effort is spread across multiple people in the development team.

Alternatives
------------

So if we don't want to use AWS, what are the alternatives? 

One option is to purchase a hardware server and keep it on premises. Managing server hardware is becoming
an increasingly specialised skillset and thus it might be challenging to find someone able to do this
professionally. Fortunately, companies like Hetzner will do it for us for a monthly fee and will provide
a dedicated server for installing anything we like. We can install Kubernetes or Proxmox or anything else
and make our own cloud based on rented server(s). Remember: there is no cloud, just the other peoples
computers.

Furthermore, there are many smaller and cheaper cloud providers that are more than enough for small-medium
scale projects (Digital Ocean, Vultr, Linode, etc.). Some consumers of AWS kool aid think that to start your
own SaaS you need 100k in AWS credits, but the reality is that many web apps can be developed to be
fairly simple and lightweight. There are indie developers spending less than $100 monthly to run a SaaS
app or website that makes them fairly good money.

