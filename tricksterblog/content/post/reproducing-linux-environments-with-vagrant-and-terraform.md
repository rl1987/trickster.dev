+++
author = "rl1987"
title = "Reproducing Linux environments with Vagrant and Terraform"
date = "2022-03-27"
tags = ["devops"]
+++

When developing and operating scraping/automation solutions, we don't exactly want to focus
on systems administration part of things. If we are writing code to achieve a particular
objective, making that code run on the VPS or local system is merely a supportive side-objective
that is required to make the primary thing happen. Thus it is undesirable to spend too much time
on it, especially if we can use automation to avoid repetitive, error-prone activity of installing
the required tooling in disposable virtual machines or virtual private servers. Luckily for us,
there are DevOps tools developed for this exact purpose. 

For the sake of this example, we will be setting up Node.js with [n8n](https://n8n.io/)
workflow automation platform.

To reproduce virtual machine with Linux system on a development machine, we will use 
[Vagrant](https://www.vagrantup.com/) VM management software with [Virtualbox](https://www.virtualbox.org/)
backend.

To reproduce the same environment in Digital Ocean VPS, we will use [Terraform](https://www.terraform.io/)
infrastructure-as-code tool.



