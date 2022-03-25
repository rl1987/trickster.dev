+++
author = "rl1987"
title = "Reproducible Linux environments with Vagrant and Terraform"
date = "2022-03-25"
tags = ["devops"]
+++

When developing and operating scraping/automation solutions, we don't exactly want to focus
on systems administration part of things. If we are writing code to achieve a particular
objective, making that code run on the VPS or local system is merely a supporting side-objective
that is required to make the primary thing happen. Thus it is undesirable to spend too much time
on it, especially if we can use automation to avoid repetitive, error-prone activity of installing
the required tooling in disposable virtual machines or virtual private servers. Luckily for us,
there are DevOps tools developed for this exact purpose. 

For the sake of this example, we will be setting up Node.js with [n8n](https://n8n.io/)
workflow automation platform.

To reproduce virtual machine with Linux OS on a development machine, we will use 
[Vagrant](https://www.vagrantup.com/) VM management software with [Virtualbox](https://www.virtualbox.org/)
backend.

To reproduce the same environment in Digital Ocean VPS, we will use [Terraform](https://www.terraform.io/)
infrastructure-as-code tool.

Vagrant
-------

First, we need to set up Vagrant. If you use any of the major desktop operating systems (Windows,
macOS, Linux) you should be able to find an installer at [Vagrant Downloads page](https://www.vagrantup.com/downloads).
You may also want to check if it is available through a package manager on your system.

Likewise, Virtualbox installers are available on [Virtualbox downloads page](https://www.virtualbox.org/wiki/Downloads).

Once both are installed, we are ready to start setting up a configuration for our VM. We go to
[Vagrant boxes search](https://app.vagrantup.com/boxes/search) - a searchable directory for pre-made
virtual machine images that we can use. Since Vagrant works best with Linux, most of these will be 
Linux-based. For the sake of this example we choose `generic/debian11` as this provides a fairly
vanilla Debian 11 system that is also readily available on cloud providers.

We need to create Vagrantfile now. This will be a central configuration file for the Vagrant
environment we will be setting up. Technically Vagrantfiles are written in Ruby, but don't
worry if you don't know Ruby - it's not actually required in all but most advanced use
cases of Vagrant.

On the [Vagrant box page](https://app.vagrantup.com/generic/boxes/debian11), 
there is a very basic example snippet:

```ruby
Vagrant.configure("2") do |config|
  config.vm.box = "generic/debian11"
end
```

However this is not enough for us. Thus we will create new Vagrantfile with more extensive
template by running `vagrant init generic/debian11` in a root directory of our project.
This creates a following Vagrantfile:

```ruby
# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://vagrantcloud.com/search.
  config.vm.box = "generic/debian11"

  # Disable automatic box update checking. If you disable this, then
  # boxes will only be checked for updates when the user runs
  # `vagrant box outdated`. This is not recommended.
  # config.vm.box_check_update = false

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  # NOTE: This will enable public access to the opened port
  # config.vm.network "forwarded_port", guest: 80, host: 8080

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine and only allow access
  # via 127.0.0.1 to disable public access
  # config.vm.network "forwarded_port", guest: 80, host: 8080, host_ip: "127.0.0.1"

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # config.vm.network "private_network", ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network "public_network"

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  # config.vm.synced_folder "../data", "/vagrant_data"

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #
  # config.vm.provider "virtualbox" do |vb|
  #   # Display the VirtualBox GUI when booting the machine
  #   vb.gui = true
  #
  #   # Customize the amount of memory on the VM:
  #   vb.memory = "1024"
  # end
  #
  # View the documentation for the provider you are using for more
  # information on available options.

  # Enable provisioning with a shell script. Additional provisioners such as
  # Ansible, Chef, Docker, Puppet and Salt are also available. Please see the
  # documentation for more information about their specific syntax and use.
  # config.vm.provision "shell", inline: <<-SHELL
  #   apt-get update
  #   apt-get install -y apache2
  # SHELL
end
```

In the initial configuration, only `config.vm.box` is set and rest is commented out.
Read the comments to get an idea of what can be configured for the virtual machine.

First, we want to perform provisioning with a shell script. However, we will not be
using inline syntax shown in the comments and will be creating a separate shell
script file instead. This is because we want to be prepared to reuse provisioning
code in Terraform config that we will work on later without introducing code
duplication. Thus we replace the provisioning section with the following line:

```ruby
  config.vm.provision "shell", path: "provision.sh"
```

Now we have to develop the shell script that will install Node.js, n8n and all the
dependencies we will need to run n8n and also launch n8n as daemon.

The contents of provision.sh file are fairly straightforward:

```shell
#!/bin/bash

set -x

apt-get update

curl -fsSL https://deb.nodesource.com/setup_17.x -o /tmp/install_node.sh
bash /tmp/install_node.sh
apt-get install -y gcc g++ make nodejs

curl -sL https://dl.yarnpkg.com/debian/pubkey.gpg | gpg --dearmor | sudo tee /usr/share/keyrings/yarnkey.gpg >/dev/null
echo "deb [signed-by=/usr/share/keyrings/yarnkey.gpg] https://dl.yarnpkg.com/debian stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
apt-get update 
apt-get install -y yarn

npm install n8n -g
npm install pm2 -g

pm2 start n8n
pm2 startup
pm2 save
```

First, we run `apt-get update` so that APT system would fetch up-to-date information about Debian packages.
Next, we proceed with Node.js installation. Since Debian package of Node.JS is not very well maintained, we
use an alternative approach of installing [NodeSource binary distribution](https://github.com/nodesource/distributions)
that involves fetching a shell script to update APT configuration, running it and installing NodeJS from
third party APT repository. We use similar approach to install Yarn package manager. There is no explicit step to 
install NPM, as it is installed from `nodejs` APT package.

Now we can use NPM to install n8n that we do through command `npm install n8n -g`. Since we want to run n8n as daemon
we also install [PM2](https://pm2.keymetrics.io/) process manager and run the relevant commands to set up n8n as
background service process. PM2 makes sure that n8n will be relaunched when Linux system is restarted.

Running `vagrant up` in the directory with Vagrantfile creates a virtual machine with Debian Linux 11 and runs our
provisioning script. Running `vagrant ssh` will give us a shell access to Linux environment that was provisioned.
We can verify that n8n is indeed running:

```
vagrant@debian11:~$ ps aux | grep n8n
root         907  7.5  9.9 11538924 201832 ?     Ssl  12:28   0:08 node /usr/bin/n8n
vagrant     1592  0.0  0.0   6152   708 pts/0    S+   12:30   0:00 grep --color=auto n8n
vagrant@debian11:~$ curl http://127.0.0.1:5678 -v
*   Trying 127.0.0.1:5678...
* Connected to 127.0.0.1 (127.0.0.1) port 5678 (#0)
> GET / HTTP/1.1
> Host: 127.0.0.1:5678
> User-Agent: curl/7.74.0
> Accept: */*
>
* Mark bundle as not supporting multiuse
< HTTP/1.1 200 OK
< X-Powered-By: Express
< Access-Control-Allow-Origin: http://localhost:8080
< Access-Control-Allow-Credentials: true
< Access-Control-Allow-Methods: GET, POST, OPTIONS, PUT, PATCH, DELETE
< Access-Control-Allow-Headers: Origin, X-Requested-With, Content-Type, Accept, sessionid
< Content-Type: text/html; charset=utf-8
< Content-Length: 1201
< ETag: W/"4b1-/hUzA+Pj4gDyZovqj340mKmXXjQ"
< Vary: Accept-Encoding
< Date: Fri, 25 Mar 2022 12:35:55 GMT
< Connection: keep-alive
< Keep-Alive: timeout=5
<
<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="/favicon.ico"><script>window.BASE_PATH = "/";</script><title>n8n.io - Workflow Automation</title><link href="/js/chunk-2d2073c1.f0370751.js" rel="prefetch"><link href="/js/chunk-2d22d3e6.388c0a4c.js" rel="prefetch"><link href="/js/chunk-4301fce8.d032a636.js" rel="prefetch"><link href="/js/chunk-b1e1f7c0.92d036f0.js" rel="prefetch"><link href="/css/app.287bd9f8.css" rel="preload" as="style"><link href="/css/chunk-vendors.29499615.css" rel="preload" as="style"><link href="/js/app.070a8ea4.js" rel="preload" as="script"><link href="/js/chunk-vendors.39458c07.js" rel="preload" as="script"><link href="/css/chunk-vendors.29499615.css" rel="stylesheet"><link href="/css/app.287bd9f8.css" rel="stylesheet"></head><body><noscript><strong>We're sorry but the n8n Editor-UI doesn't work properly without JavaScript enabled. Pl* Connection #0 to host 127.0.0.1 left intact
ease enable it to continue.</strong></noscript><div id="app"></div><script src="/js/chunk-vendors.39458c07.js"></script><script src="/js/app.070a8ea4.js"></script></body></html>
```

We can also verify presence of Node.js tooling:

```
vagrant@debian11:~$ node --version
v17.8.0
vagrant@debian11:~$ yarn --version
1.22.18
vagrant@debian11:~$ npm --version
8.5.5
vagrant@debian11:~$ node
Welcome to Node.js v17.8.0.
Type ".help" for more information.
> .exit
```

However, we cannot access n8n through a desktop web browser from host system. That's because we did not configure port forwarding
in our Vagrantfile.

We edit port forwarding section to add the following line:

```ruby
  config.vm.network "forwarded_port", guest: 5678, host: 5678
```

To reboot the VM and make this change working, we run `vagrant reload`. After doing so, we can access n8n frontend via http://localhost:5678/.

There is one more thing we need to set up in Vagrant configuration. You may want to edit your source code through VIM or other
text editor in host machine and run it in a guest machine without going through the hassle of using SFTP to transfer files.
Vagrant supports shared directories that enable us to mirror a source code directory between host and guest systems. Edit the part
of Vagrantfile that mentions shared folders to add the following line:

```ruby
  config.vm.synced_folder ".", "/vagrant"
```

This will make current source code directory on host machine mirrored to /vagrant in guest machine.
To make this change work, we need to run `vagrant reload` again. However, depending on exact circumstances
this may not work right away. To fix it, you may need to install `vbguest` plugin and activate by running the following
commands:

```
$ vagrant plugin install vagrant-vbguest
$ vagrant vbguest
$ vagrant reload
```

To temporarily shut down your Vagrant VM, run:

```
$ vagrant halt
```

To delete the VM, run:

```
$ vagrant destroy
```

Complete Vagrantfile with comments removed for brevity is merely few lines long:

```ruby
Vagrant.configure("2") do |config|
  config.vm.box = "generic/debian11"
  config.vm.network "forwarded_port", guest: 5678, host: 5678
  config.vm.synced_folder ".", "/vagrant"
  config.vm.provision "shell", path: "provision.sh"
end
```

With less than 30 lines of code were able to set up an entire environment for experimenting with n8n automation workflows
in a reproducible way. This enables us to delete the VM when no longer needed, but quickly recreate it from Vagrantfile
and provisioning script when we need it again. 

Terraform
---------

Terraform is another DevOps tool created by Hashicorp - the company that developed Vagrant. It reads declarative configuration
files written in HCL (Hashicorp Configuration Language) and performs infrastructure setup for us. We will use it to provision
a Digital Ocean VPS with the same environment we created in Vagrant VM. The following steps will use Terraform CLI tool
that can be found at [Terraform Downloads page](https://www.terraform.io/downloads).

There are some prerequisites before we start. You will need to have a Digital Ocean account with payment method added.
Furthermore, you will need to register your SSH key on your Digital Ocean account if you haven't already (this is generally
convenient thing to have, as you won't need to type a password in when logging into servers from your local machine).
Lastly, you will need to generate Digital Ocean API token and save it to do_token.txt (make sure there's no whitespace!).

When these matters are take care of, we can start writing our main.tf file that will contain the configuration for 
the server. We start by setting up [Digital Ocean Terraform provider](https://registry.terraform.io/providers/digitalocean/digitalocean/latest/docs) 
(an equivalent of software library that abstract away an external API) with the following lines:

```hcl
terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

provider "digitalocean" {
  token = file("do_token.txt")
}

```

Next, we create a resource (an equivalent of object) for Digital Ocean droplet we want created:

```hcl
resource "digitalocean_droplet" "n8n" {
  image     = "debian-11-x64"
  name      = "n8n"
  region    = "sfo3"
  size      = "s-1vcpu-1gb"
  user_data = file("provision.sh")
  ssh_keys  = ["[REDACTED]"]
}

```

There are several things of interest here. We set `image` argument to `debian-11-x64`
as this is the same Linux distribution that we had in our Vagrant machine. Thus it is
very reasonable to expect that our provisioning script will work here as well.
We set `size` to value that corresponds to $5/month droplet as we don't expect to
use much resources. I find that in many cases $5/month droplets are more than enough
for computational needs of many scraping/automation scripts that I develop.
Next, we set up SSH key fingerprint that will be needed to access the droplet.
We make sure to use the same SSH keypair that is configured in Digital
Ocean account and our local machine. Also we set `user_data` with contents of our
provisioning script so that it will be launched when server setup is complete.

Lastly, we create an output for getting an IP address of server after setup:

```hcl
output "server_ip" {
  value = resource.digitalocean_droplet.n8n.ipv4_address
}
```

To actually install our environment on the cloud, there are three steps. First, we
run `terraform init` to initialize local state with TF providers. Next, we launch
`terraform plan -out=tf.plan` to set up an action plan that will be shown for us
and saved into file tf.plan. Lastly, we run `terraform apply tf.plan` to actually
proceed with the installation. Few minutes later, we can access n8n via HTTP
protocol at port 5678 on IP address that is printed at the end of the installation
process. 

Conveniently for us, Digital Ocean does not set up any default firewall
rules that would limit the ingress traffic. However if you work on equivalent 
setup with AWS EC2 you would need to make sure that a security group is configured
accordingly. Furthermore, you may want to set up HTTP authentication for n8n
by setting up `N8N_BASIC_AUTH_ACTIVE` environment variable to `true` in
provision.sh file and setting username/password to `N8N_BASIC_AUTH_USER` \ 
`N8N_BASIC_AUTH_PASSWORD` variables if you are going to run it on the cloud for
non-trivial amounts of time (this has been skipped in above code for simplicity).

When we no longer need this environment, we can run `terraform destroy` to remove
it.

The complete main.tf file is as follows:

```hcl
terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

provider "digitalocean" {
  token = file("do_token.txt")
}

resource "digitalocean_droplet" "n8n" {
  image     = "debian-11-x64"
  name      = "n8n"
  region    = "sfo3"
  size      = "s-1vcpu-1gb"
  user_data = file("provision.sh")
  ssh_keys  = ["[REDACTED]"]
}

output "server_ip" {
  value = resource.digitalocean_droplet.n8n.ipv4_address
}

```

Since the new environment is now running on the remote server it is not very feasible to make
a shared directory with it. However, if we wanted to upload some files to the server
we could have used [`file` provisioner](https://www.terraform.io/language/resources/provisioners/file)
to do so.

$5/month Digital Ocean droplet costs $0.007 per hour. If we launch some automation workflow 
in the evening and let it run overnight for 10 hours, we have merely spent $0.07!
Since Terraform enables us to prepare configuration once and setup/destroy the environment
as many times as we like, we can save money that we would otherwise spending on keeping
the unused infra running in the cloud. Furthermore, we save time and effort that we would
be spending when recreating the environment repeatedly and possibly making mistakes.

