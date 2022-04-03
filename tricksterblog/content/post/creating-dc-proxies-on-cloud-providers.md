+++
author = "rl1987"
title = "Creating DC proxies on cloud providers"
date = "2022-04-04"
draft = true
tags = ["automation", "python", "growth-hacking", "security", "bug-bounties"]
+++

Although many proxy providers offer data center (DC) proxies fairly cheaply, sometimes it is desirable
to make our own. In this post we will discuss how to set up [Squid](http://www.squid-cache.org/) proxy
server on cheap Virtual Private Servers from [Vultr](https://www.vultr.com/). We will be using Debian 11
Linux environment on virtual "Cloud Compute" servers.

Let us go through the steps to install Squid through Linux shell with commands that will be put into provisioning script.

First, we need to install the required APT packages:

```
$ apt-get update
$ apt-get install -y squid apache2-utils
```

Besides Squid, we also install Apache utils package to get a htpasswd(1) tool that will create file for Basic HTTP authentication.

Let's enable squid service to make sure it gets re-launched during server reboot:

```
$ systemctl enable squid
```

Now we need to edit configuration file at /etc/squid/squid.conf. Since we want to all incoming HTTP traffic we remove
line that disallows it:

```
$ sed -i 's/http_access deny all//' /etc/squid/squid.conf
```

This used sed(1) to remove line `http_access deny all`. Now let us configure HTTP proxying with username/password authentication.
We add several lines to configuration file for this purpose:

```
$ echo "auth_param basic program /usr/lib/squid3/basic_ncsa_auth /etc/squid/passwords" >> /etc/squid/squid.conf
$ echo "auth_param basic realm proxy" >> /etc/squid/squid.conf
$ echo "acl authenticated proxy_auth REQUIRED" >> /etc/squid/squid.conf
$ echo "http_access allow authenticated" >> /etc/squid/squid.conf
```

This configures Squid to accept incoming requests with HTTP Basic Auth. Let's restart the squid to get it to read modified
configuration:

```
$ systemctl reload squid
```

At this point Squid is reachable from within the server, but not from outside. This is because by default Vultr Debian servers
have Netfilter firewall enabled that only allows SSH traffic to go in. To disable the firewall, we need to run:

```
$ ufw disable
```

Now we can use the proxy server from some other program or script to relay traffic.

The entire provisioning script is as follows:

```shell
#!/bin/bash

apt-get update
apt-get install -y squid apache2-utils

systemctl enable squid

# Based on: https://stackoverflow.com/questions/3297196/how-to-set-up-a-squid-proxy-with-basic-username-and-password-authentication
sed -i 's/http_access deny all//' /etc/squid/squid.conf
echo "auth_param basic program /usr/lib/squid3/basic_ncsa_auth /etc/squid/passwords" >> /etc/squid/squid.conf
echo "auth_param basic realm proxy" >> /etc/squid/squid.conf
echo "acl authenticated proxy_auth REQUIRED" >> /etc/squid/squid.conf
echo "http_access allow authenticated" >> /etc/squid/squid.conf

htpasswd -bc /etc/squid/passwords user trust_no_1

systemctl reload squid

ufw disable

```

Note that you should probably change the hardcoded password in the script to a more secure one.

Once we boot up a Vultr VPS with Debian 11 Linux we can upload this script through SFTP and launch it there. However what if we
want to set up multiple proxy servers? Luckily for us, Vultr has it's own official 
[Terraform provider](https://registry.terraform.io/providers/vultr/vultr/latest/docs) and we can use Terraform
infrastructure-as-code tool for automated server provisioning. We need to write some code in HCL - Hashicorp Configuration
Language in main.tf file. 

Before we proceed with developing Terraform configuration, we need to get Vultr API key from [SSH keys](https://my.vultr.com/settings/#settingssshkeys)
tab in Account Settings part of Vultr client area.

First, let us import and configure the Vultr provider:

```hcl
terraform {
  required_providers {
    vultr = {
      source  = "vultr/vultr"
      version = "2.10.1"
    }
  }
}

provider "vultr" {
  # Setting api_key is not required if VULTR_API_KEY environment variable is present with API key value.
  #api_key = "[REDACTED]"
}
```

To make server troubleshooting more convenient, let us set up SSH key resource with our public SSH key. This will let us
establish SSH connection from the current development machine without worrying about SSH username/password.

```hcl
resource "vultr_ssh_key" "my_ssh_key" {
  name    = "my-ssh-key"
  ssh_key = file("~/.ssh/id_rsa.pub")
}
```

This is not strictly necessary as we can simply access Linux shell through Vultr console, but will make things nicer to debug
if the need arises.

Next, we set a variable for proxy count with default value of 8.

```hcl
variable "proxy_count" {
  default = 8
}
```

Now it's the most important part - setting up resources for the actual proxy servers. The code that declaratively specifies
the server configuration is the following:

```hcl
resource "vultr_instance" "proxy" {
  count       = var.proxy_count
  plan        = "vc2-1c-1gb"
  region      = "sea"
  os_id       = 477
  ssh_key_ids = [vultr_ssh_key.my_ssh_key.id]
  user_data   = file("provision.sh")
}

```

We set proxy server count by referencing the value of variable we created earlier. We set `plan`, `region` and `os_id` to values
we got from the following Vultr APIs:

* [List Plans](https://www.vultr.com/api/#operation/list-plans)
* [List Regions](https://www.vultr.com/api/#operation/list-regions)
* [List OS](https://www.vultr.com/api/#operation/list-os)

The `plan` value `vc2-1c-1gb` corresponds to small VPS that costs $5/month, `sea` corresponds to Seattle region and 477 is for
Debian Linux 11. We set `ssh_key_ids` with UUID of SSH key that was configured earlier to make the server allow incoming
SSH connections from our machine. Lastly we set `user_data` with the contents of our provisioning script. This might seem to
be puzzling. The thing is, Vultr and many cloud provider install Linux servers with a program called 
[cloud-init](https://cloudinit.readthedocs.io/en/latest/) that is meant to provision and configure newly launched server.
It takes either a YAML file or a script that it will execute. 

Last thing we do in our Terraform configuration file is declaring an output for IP addresses of newly created servers:

```hcl
output "proxy_ip" {
  value = ["${vultr_instance.proxy.*.main_ip}"]
}
```

The complete main.tf file is as follows:

```hcl
terraform {
  required_providers {
    vultr = {
      source  = "vultr/vultr"
      version = "2.10.1"
    }
  }
}

provider "vultr" {
  # Setting api_key is not required if VULTR_API_KEY environment variable is present with API key value.
  #api_key = "[REDACTED]"
}

resource "vultr_ssh_key" "my_ssh_key" {
  name    = "my-ssh-key"
  ssh_key = file("~/.ssh/id_rsa.pub")
}

variable "proxy_count" {
  default = 8
}

resource "vultr_instance" "proxy" {
  count       = var.proxy_count
  plan        = "vc2-1c-1gb"
  region      = "sea"
  os_id       = 477
  ssh_key_ids = [vultr_ssh_key.my_ssh_key.id]
  user_data   = file("provision.sh")
}

output "proxy_ip" {
  value = ["${vultr_instance.proxy.*.main_ip}"]
}

```

When using the common Terraform CLI commands note that `terraform apply` finishes sooner than the actual
provisioning of the server. Few minutes later, we can verify that proxies indeed work:

```
$ curl --proxy-basic --proxy-user user:trust_no_1 --proxy http://66.42.65.58:3128 http://ifconfig.me -v
*   Trying 66.42.65.58:3128...
* Connected to 66.42.65.58 (66.42.65.58) port 3128 (#0)
* Proxy auth using Basic with user 'user'
> GET http://ifconfig.me/ HTTP/1.1
> Host: ifconfig.me
> Proxy-Authorization: Basic dXNlcjp0cnVzdF9ub18x
> User-Agent: curl/7.77.0
> Accept: */*
> Proxy-Connection: Keep-Alive
>
* Mark bundle as not supporting multiuse
< HTTP/1.1 200 OK
< access-control-allow-origin: *
< Content-Type: text/plain; charset=utf-8
< Content-Length: 11
< Date: Sun, 03 Apr 2022 18:38:08 GMT
< x-envoy-upstream-service-time: 1
< X-Cache: MISS from vultr
< X-Cache-Lookup: MISS from vultr:3128
< Via: 1.1 google, 1.1 vultr (squid/4.13)
< Connection: keep-alive
<
* Connection #0 to host 66.42.65.58 left intact
66.42.65.58
```

