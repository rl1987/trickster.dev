+++
author = "rl1987"
title = "Recon-ng: modular framework for OSINT automation"
date = "2022-09-07"
tags = ["automation", "security", "bug-bounties", "osint"]
+++

OSINT is collection and analysis of information from public sources. Nowadays it
can largely be automated through web scraping and API integrations.
[Recon-ng](https://github.com/lanmaster53/recon-ng) is open source OSINT framework
that features a modular architecture. Each module can be thought as a pluggable
piece of code that can be loaded on as-needed basis. Most modules are API integrations
and scrapers of data sources. Some deal with report generation and other auxillary tasks.
Since recon-ng was developed by and for infosec people, the user interface resembles
that of Metasploit Framework, thus making the learning curve easier to people who
are working on the offensive side of cybersecurity.

Some security-centric Linux distributions ship recon-ng on their package managers.
Furthermore, macOS users can install it through Homebrew. If none of these options
are applicable one can simply run it from source code in a fairly vanilla Python
dev environment.

The recon-ng script gives us a command line for running OSINT tasks:

```
$ recon-ng

    _/_/_/    _/_/_/_/    _/_/_/    _/_/_/    _/      _/            _/      _/    _/_/_/
   _/    _/  _/        _/        _/      _/  _/_/    _/            _/_/    _/  _/       
  _/_/_/    _/_/_/    _/        _/      _/  _/  _/  _/  _/_/_/_/  _/  _/  _/  _/  _/_/_/
 _/    _/  _/        _/        _/      _/  _/    _/_/            _/    _/_/  _/      _/ 
_/    _/  _/_/_/_/    _/_/_/    _/_/_/    _/      _/            _/      _/    _/_/_/    


                                          /\
                                         / \\ /\
    Sponsored by...               /\  /\/  \\V  \/\
                                 / \\/ // \\\\\ \\ \/\
                                // // BLACK HILLS \/ \\
                               www.blackhillsinfosec.com

                  ____   ____   ____   ____ _____ _  ____   ____  ____
                 |____] | ___/ |____| |       |   | |____  |____ |
                 |      |   \_ |    | |____   |   |  ____| |____ |____
                                   www.practisec.com

                      [recon-ng v5.1.2, Tim Tomes (@lanmaster53)]                       

[85] Recon modules
[13] Disabled modules
[8]  Reporting modules
[4]  Import modules
[2]  Exploitation modules
[2]  Discovery modules

[recon-ng][default] > 
```

At this point it is likely to print bunch of errors about missing API keys
and some Python modules you are advised to install. It is okay to disregard
these when starting. We still have stuff to try out at this point.

Let us get familiar with the concept of workspaces. In recon-ng, a workspace
is basically a project that holds together various pieces of data you collect.
When you launch recon-ng you will be assigned a default workspace. Let us switch
create new workspace and switch to it:

```
[recon-ng][default] > workspaces create test
[recon-ng][test] > 
```

`workspaces list` command lists all the available workspaces:

```
[recon-ng][test] > workspaces list

  +----------------------------------+
  | Workspaces |       Modified      |
  +----------------------------------+
  | default    | 2022-09-05 11:30:15 |
  | test       | 2022-09-05 11:55:27 |
  +----------------------------------+

```

If we wanted to go back to default workspaces, we can say `workspaces load default`.
To remove a workspace we no longer need we can say `workspaces remove`.

Like mentioned before, a recon-ng module is pluggable piece of code that can loaded
when needed. All the modules are stored in a separate git repo called 
[recon-ng-marketplace](https://github.com/lanmaster53/recon-ng-marketplace). Run
`marketplace install all` to download them into a local installation.
When that is done, running `marketplace search` will give you a table with
available modules. Running `modules list` will give you list of modules
by category. To search modules by keyword, we can run these commands
with the keyword:

```
[recon-ng][test] > modules search domain
[*] Searching installed modules for 'domain'...

  Recon
  -----
    recon/companies-domains/censys_subdomains
    recon/companies-domains/pen
    recon/companies-domains/viewdns_reverse_whois
    recon/companies-domains/whoxy_dns
    recon/contacts-domains/migrate_contacts
    recon/domains-companies/pen
    recon/domains-companies/whoxy_whois
    recon/domains-contacts/hunter_io
    recon/domains-contacts/pen
    recon/domains-contacts/pgp_search
    recon/domains-contacts/whois_pocs
    recon/domains-contacts/wikileaker
    recon/domains-credentials/pwnedlist/api_usage
    recon/domains-credentials/pwnedlist/domain_ispwned
    recon/domains-credentials/pwnedlist/leak_lookup
    recon/domains-credentials/pwnedlist/leaks_dump
    recon/domains-domains/brute_suffix
    recon/domains-hosts/binaryedge
    recon/domains-hosts/bing_domain_api
    recon/domains-hosts/bing_domain_web
    recon/domains-hosts/brute_hosts
    recon/domains-hosts/builtwith
    recon/domains-hosts/certificate_transparency
    recon/domains-hosts/google_site_web
    recon/domains-hosts/hackertarget
    recon/domains-hosts/mx_spf_ip
    recon/domains-hosts/netcraft
    recon/domains-hosts/shodan_hostname
    recon/domains-hosts/spyse_subdomains
    recon/domains-hosts/ssl_san
    recon/domains-hosts/threatcrowd
    recon/domains-hosts/threatminer
    recon/domains-vulnerabilities/ghdb
    recon/domains-vulnerabilities/xssed
    recon/hosts-domains/migrate_hosts

[recon-ng][test] > marketplace search domain
[*] Searching module index for 'domain'...

  +-----------------------------------------------------------------------------------------------+
  |                        Path                        | Version |   Status  |  Updated   | D | K |
  +-----------------------------------------------------------------------------------------------+
  | discovery/info_disclosure/cache_snoop              | 1.1     | installed | 2020-10-13 |   |   |
  | recon/companies-domains/censys_subdomains          | 2.0     | installed | 2021-05-10 | * | * |
  | recon/companies-domains/pen                        | 1.1     | installed | 2019-10-15 |   |   |
  | recon/companies-domains/viewdns_reverse_whois      | 1.1     | installed | 2021-08-24 |   |   |
  | recon/companies-domains/whoxy_dns                  | 1.1     | installed | 2020-06-17 |   | * |
  | recon/companies-hosts/censys_tls_subjects          | 2.0     | disabled  | 2021-05-11 | * | * |
  | recon/contacts-domains/migrate_contacts            | 1.1     | installed | 2020-05-17 |   |   |
  | recon/domains-companies/censys_companies           | 2.0     | disabled  | 2021-05-10 | * | * |
  | recon/domains-companies/pen                        | 1.1     | installed | 2019-10-15 |   |   |
  | recon/domains-companies/whoxy_whois                | 1.1     | installed | 2020-06-24 |   | * |
  | recon/domains-contacts/hunter_io                   | 1.3     | installed | 2020-04-14 |   | * |
  | recon/domains-contacts/metacrawler                 | 1.1     | disabled  | 2019-06-24 | * |   |
  | recon/domains-contacts/pen                         | 1.1     | installed | 2019-10-15 |   |   |
  | recon/domains-contacts/pgp_search                  | 1.4     | installed | 2019-10-16 |   |   |
  | recon/domains-contacts/whois_pocs                  | 1.0     | installed | 2019-06-24 |   |   |
  | recon/domains-contacts/wikileaker                  | 1.0     | installed | 2020-04-08 |   |   |
  | recon/domains-credentials/pwnedlist/account_creds  | 1.0     | disabled  | 2019-06-24 | * | * |
  | recon/domains-credentials/pwnedlist/api_usage      | 1.0     | installed | 2019-06-24 |   | * |
  | recon/domains-credentials/pwnedlist/domain_creds   | 1.0     | disabled  | 2019-06-24 | * | * |
  | recon/domains-credentials/pwnedlist/domain_ispwned | 1.0     | installed | 2019-06-24 |   | * |
  | recon/domains-credentials/pwnedlist/leak_lookup    | 1.0     | installed | 2019-06-24 |   |   |
  | recon/domains-credentials/pwnedlist/leaks_dump     | 1.0     | installed | 2019-06-24 |   | * |
  | recon/domains-domains/brute_suffix                 | 1.1     | installed | 2020-05-17 |   |   |
  | recon/domains-hosts/binaryedge                     | 1.2     | installed | 2020-06-18 |   | * |
  | recon/domains-hosts/bing_domain_api                | 1.0     | installed | 2019-06-24 |   | * |
  | recon/domains-hosts/bing_domain_web                | 1.1     | installed | 2019-07-04 |   |   |
  | recon/domains-hosts/brute_hosts                    | 1.0     | installed | 2019-06-24 |   |   |
  | recon/domains-hosts/builtwith                      | 1.1     | installed | 2021-08-24 |   | * |
  | recon/domains-hosts/censys_domain                  | 2.0     | disabled  | 2021-05-10 | * | * |
  | recon/domains-hosts/certificate_transparency       | 1.2     | installed | 2019-09-16 |   |   |
  | recon/domains-hosts/google_site_web                | 1.0     | installed | 2019-06-24 |   |   |
  | recon/domains-hosts/hackertarget                   | 1.1     | installed | 2020-05-17 |   |   |
  | recon/domains-hosts/mx_spf_ip                      | 1.0     | installed | 2019-06-24 |   |   |
  | recon/domains-hosts/netcraft                       | 1.1     | installed | 2020-02-05 |   |   |
  | recon/domains-hosts/shodan_hostname                | 1.1     | installed | 2020-07-01 | * | * |
  | recon/domains-hosts/spyse_subdomains               | 1.1     | installed | 2021-08-24 |   | * |
  | recon/domains-hosts/ssl_san                        | 1.0     | installed | 2019-06-24 |   |   |
  | recon/domains-hosts/threatcrowd                    | 1.0     | installed | 2019-06-24 |   |   |
  | recon/domains-hosts/threatminer                    | 1.0     | installed | 2019-06-24 |   |   |
  | recon/domains-vulnerabilities/ghdb                 | 1.1     | installed | 2019-06-26 |   |   |
  | recon/domains-vulnerabilities/xssed                | 1.1     | installed | 2020-10-18 |   |   |
  | recon/hosts-domains/migrate_hosts                  | 1.1     | installed | 2020-05-17 |   |   |
  | recon/hosts-hosts/censys_query                     | 2.0     | disabled  | 2021-05-10 | * | * |
  | recon/hosts-hosts/virustotal                       | 1.0     | installed | 2019-06-24 |   | * |
  | recon/netblocks-hosts/virustotal                   | 1.0     | installed | 2019-06-24 |   | * |
  +-----------------------------------------------------------------------------------------------+

  D = Has dependencies. See info for details.
  K = Requires keys. See info for details.

[recon-ng][test] > 
```

We can see that some modules require API keys and/or additional dependencies to be used.
Running `marketplace info` on a module path describes the module:

```
[recon-ng][test] > marketplace info recon/domains-hosts/google_site_web  

  +---------------------------------------------------------------------------------------------------------------------------------+
  | path          | recon/domains-hosts/google_site_web                                                                             |
  | name          | Google Hostname Enumerator                                                                                      |
  | author        | Tim Tomes (@lanmaster53)                                                                                        |
  | version       | 1.0                                                                                                             |
  | last_updated  | 2019-06-24                                                                                                      |
  | description   | Harvests hosts from Google.com by using the 'site' search operator. Updates the 'hosts' table with the results. |
  | required_keys | []                                                                                                              |
  | dependencies  | []                                                                                                              |
  | files         | []                                                                                                              |
  | status        | installed                                                                                                       |
  +---------------------------------------------------------------------------------------------------------------------------------+

```

Let us try using this module for subdomain enumerator given a seed domain. Running
`modules load` command with the module path activates the modules and gives us a
subshell for running commands within context of the module.

```
[recon-ng][test] > modules load recon/domains-hosts/google_site_web 
[recon-ng][test][google_site_web] > 
```

For example, running `info` gives us a simple description on the current module
and it's parameters.


```
recon-ng][test][google_site_web] > info

      Name: Google Hostname Enumerator
    Author: Tim Tomes (@lanmaster53)
   Version: 1.0

Description:
  Harvests hosts from Google.com by using the 'site' search operator. Updates the 'hosts' table with
  the results.

Options:
  Name    Current Value  Required  Description
  ------  -------------  --------  -----------
  SOURCE  default        yes       source of input (see 'info' for details)

Source Options:
  default        SELECT DISTINCT domain FROM domains WHERE domain IS NOT NULL
  <string>       string representing a single input
  <path>         path to a file containing a list of inputs
  query <sql>    database query returning one column of inputs

```

Let us set the `SOURCE` option to a domain of a company that has an open
[bug bounty program](https://hackerone.com/tencent?type=team) and run the
module. 

```
[recon-ng][test][google_site_web] > options set SOURCE tencent.com
SOURCE => tencent.com
[recon-ng][test][google_site_web] > run

-----------
TENCENT.COM
-----------
[*] Searching Google for: site:tencent.com
[*] Country: None
[*] Host: buy.cloud.tencent.com
[*] Ip_Address: None
[*] Latitude: None
[*] Longitude: None
[*] Notes: None
[*] Region: None
[*] --------------------------------------------------
[*] Country: None
[*] Host: intl.cloud.tencent.com
[*] Ip_Address: None
[*] Latitude: None
[*] Longitude: None
[*] Notes: None
[*] Region: None

...
[*] Searching Google for: site:tencent.com -site:buy.cloud.tencent.com -site:intl.cloud.tencent.com -site:meeting.tencent.com -site:open.tencent.com -site:tdesign.tencent.com -site:s.tencent.com -site:dnspod.cloud.tencent.com -site:www.tencent.com -site:ioa.tencent.com -site:market.cloud.tencent.com -site:ad.tencent.com -site:xiaowei.tencent.com -site:spd.tencent.com -site:opensource.tencent.com -site:isux.tencent.com -site:hiflow.tencent.com -site:tmc.tencent.com -site:ur.tencent.com -site:partner.cloud.tencent.com -site:ieg.tencent.com -site:app.cloud.tencent.com -site:8000.tencent.com -site:drug.ai.tencent.com -site:code.tencent.com -site:cloud.tencent.com -site:mxd.tencent.com -site:tea-lab.tencent.com -site:retail.tencent.com -site:careers.tencent.com -site:gss.tencent.com -site:todo.tencent.com -site:gameinstitute.tencent.com -site:broker.tencent.com -site:tapd.tencent.com -site:light.mofyi.tencent.com -site:tdw.tencent.com -site:aiarena.tencent.com -site:developers.tencent.com -site:om.tencent.com -site:keenlab.tencent.com -site:gwb.tencent.com -site:service.security.tencent.com -site:cdc.tencent.com -site:mtp.tencent.com -site:calendar.tencent.com -site:design.tencent.com -site:ess.tencent.com -site:gcloud.tencent.com -site:dsic.tencent.com -site:tengshi.tencent.com -site:matrix.tencent.com -site:research.tencent.com -site:jarvislab.tencent.com -site:x5.tencent.com -site:rtx.tencent.com -site:aidata.tencent.com -site:fapiao.tencent.com -site:beacon.tencent.com -site:edu.tencent.com -site:tcaplusdb.tencent.com -site:cii.tencent.com -site:healthcare.tencent.com -site:wemake.tencent.com -site:ai.tencent.com -site:security.tencent.com -site:arc.tencent.com -site:idc.tencent.com -site:quantum.tencent.com -site:tosp.tencent.com -site:en.security.tencent.com -site:app.v.tencent.com -site:blade.tencent.com -site:ipr.tencent.com -site:multimedia.tencent.com -site:jubao.tencent.com -site:xlab.tencent.com
[*] Country: None
[*] Host: tengyun.tencent.com
[*] Ip_Address: None
[*] Latitude: None
[*] Longitude: None
[*] Notes: None
[*] Region: None
[*] --------------------------------------------------
[*] Country: None
[*] Host: supplier.tencent.com
[*] Ip_Address: None
[*] Latitude: None
[*] Longitude: None
[*] Notes: None
[*] Region: None
[*] --------------------------------------------------
[*] Country: None
[*] Host: yzt.tencent.com
[*] Ip_Address: None
[*] Latitude: None
[*] Longitude: None
[*] Notes: None
[*] Region: None

...

[*] Searching Google for: site:tencent.com -site:buy.cloud.tencent.com -site:intl.cloud.tencent.com -site:meeting.tencent.com -site:open.tencent.com -site:tdesign.tencent.com -site:s.tencent.com -site:dnspod.cloud.tencent.com -site:www.tencent.com -site:ioa.tencent.com -site:market.cloud.tencent.com -site:ad.tencent.com -site:xiaowei.tencent.com -site:spd.tencent.com -site:opensource.tencent.com -site:isux.tencent.com -site:hiflow.tencent.com -site:tmc.tencent.com -site:ur.tencent.com -site:partner.cloud.tencent.com -site:ieg.tencent.com -site:app.cloud.tencent.com -site:8000.tencent.com -site:drug.ai.tencent.com -site:code.tencent.com -site:cloud.tencent.com -site:mxd.tencent.com -site:tea-lab.tencent.com -site:retail.tencent.com -site:careers.tencent.com -site:gss.tencent.com -site:todo.tencent.com -site:gameinstitute.tencent.com -site:broker.tencent.com -site:tapd.tencent.com -site:light.mofyi.tencent.com -site:tdw.tencent.com -site:aiarena.tencent.com -site:developers.tencent.com -site:om.tencent.com -site:keenlab.tencent.com -site:gwb.tencent.com -site:service.security.tencent.com -site:cdc.tencent.com -site:mtp.tencent.com -site:calendar.tencent.com -site:design.tencent.com -site:ess.tencent.com -site:gcloud.tencent.com -site:dsic.tencent.com -site:tengshi.tencent.com -site:matrix.tencent.com -site:research.tencent.com -site:jarvislab.tencent.com -site:x5.tencent.com -site:rtx.tencent.com -site:aidata.tencent.com -site:fapiao.tencent.com -site:beacon.tencent.com -site:edu.tencent.com -site:tcaplusdb.tencent.com -site:cii.tencent.com -site:healthcare.tencent.com -site:wemake.tencent.com -site:ai.tencent.com -site:security.tencent.com -site:arc.tencent.com -site:idc.tencent.com -site:quantum.tencent.com -site:tosp.tencent.com -site:en.security.tencent.com -site:app.v.tencent.com -site:blade.tencent.com -site:ipr.tencent.com -site:multimedia.tencent.com -site:jubao.tencent.com -site:xlab.tencent.com -site:tengyun.tencent.com -site:supplier.tencent.com -site:yzt.tencent.com -site:rfq.tencent.com -site:moa.tencent.com -site:growing.tencent.com -site:we.tencent.com -site:youshu.tencent.com -site:cloudsec.tencent.com -site:yunding.tencent.com -site:dmp.tencent.com -site:privacy.tencent.com -site:rg.tencent.com -site:agency.tencent.com -site:tpa.tencent.com -site:tssp.tencent.com -site:hebao.tencent.com -site:yixing.tencent.com -site:sign2.tencent.com -site:tfdp.tencent.com
[!] Google CAPTCHA triggered. No bypass available.

-------
SUMMARY
-------
[*] 96 total (96 new) hosts found.
```

We see that the modules incrementally discovers new subdomains by using `site:`
operator to get Google search results matching the seed domain, but also
using minus sign to remove the already known subdomains from search result
pages. It was able to scrape 96 subdomains before running into captcha that
Google gives the user to solve when it detects too many search requests too
quickly from single IP address. To see all the data it got so far we can
run `show hosts`.

At this point we have a bunch of subdomains, but no IP addresses related to
them. We can enrich the data in the hosts table by loading and running another 
module that will perform DNS requests for the subdomains:

```
[recon-ng][test][google_site_web] > modules load recon/hosts-hosts/resolve
[recon-ng][test][resolve] > info

      Name: Hostname Resolver
    Author: Tim Tomes (@lanmaster53)
   Version: 1.0

Description:
  Resolves the IP address for a host. Updates the 'hosts' table with the results.

Options:
  Name    Current Value  Required  Description
  ------  -------------  --------  -----------
  SOURCE  default        yes       source of input (see 'info' for details)

Source Options:
  default        SELECT DISTINCT host FROM hosts WHERE host IS NOT NULL AND ip_address IS NULL
  <string>       string representing a single input
  <path>         path to a file containing a list of inputs
  query <sql>    database query returning one column of inputs

Comments:
  * Note: Nameserver must be in IP form.

[recon-ng][test][resolve] > run
[*] buy.cloud.tencent.com => 158.79.1.174
[*] buy.cloud.tencent.com => 158.79.1.160
[*] intl.cloud.tencent.com => 158.79.1.160
[*] intl.cloud.tencent.com => 158.79.1.174
[*] meeting.tencent.com => 203.205.137.236
[*] open.tencent.com => 129.226.107.102
[*] open.tencent.com => 129.226.106.5
[*] tdesign.tencent.com => 158.79.1.56
[*] tdesign.tencent.com => 158.79.1.178
[*] tdesign.tencent.com => 158.79.1.187
[*] tdesign.tencent.com => 158.79.1.185
[*] s.tencent.com => 43.135.106.184
[*] s.tencent.com => 43.135.106.117
[*] dnspod.cloud.tencent.com => 42.194.253.127
[*] www.tencent.com => 43.152.54.219
[*] www.tencent.com => 43.152.56.217
[*] ioa.tencent.com => 119.28.121.91
[*] market.cloud.tencent.com => 183.2.144.115
...
```

Running `show hosts` again will show us that `ip_address` column is now filled.
Internally each workspace will have SQLite database for persisting the data and
the recon-ng command line gives us a way to run SQL queries on it:

```
[recon-ng][test][resolve] > db
Interfaces with the workspace's database

Usage: db <delete|insert|notes|query|schema> [...]

[recon-ng][test][resolve] > db query SELECT * FROM hosts LIMIT 10;

  +----------------------------------------------------------------------------------------------------------------+
  |           host           |    ip_address   | region | country | latitude | longitude | notes |      module     |
  +----------------------------------------------------------------------------------------------------------------+
  | buy.cloud.tencent.com    | 158.79.1.174    |        |         |          |           |       | google_site_web |
  | intl.cloud.tencent.com   | 158.79.1.160    |        |         |          |           |       | google_site_web |
  | meeting.tencent.com      | 203.205.137.236 |        |         |          |           |       | google_site_web |
  | open.tencent.com         | 129.226.107.102 |        |         |          |           |       | google_site_web |
  | tdesign.tencent.com      | 158.79.1.56     |        |         |          |           |       | google_site_web |
  | s.tencent.com            | 43.135.106.184  |        |         |          |           |       | google_site_web |
  | dnspod.cloud.tencent.com | 42.194.253.127  |        |         |          |           |       | google_site_web |
  | www.tencent.com          | 43.152.54.219   |        |         |          |           |       | google_site_web |
  | ioa.tencent.com          | 119.28.121.91   |        |         |          |           |       | google_site_web |
  | market.cloud.tencent.com | 183.2.144.115   |        |         |          |           |       | google_site_web |
  +----------------------------------------------------------------------------------------------------------------+

[*] 10 rows returned
```

For further analysis of data outside recon-ng command line we can take a snapshot
of the database:

```
[recon-ng][test][resolve] > back
[recon-ng][test] > snapshots take
[*] Snapshot created: snapshot_20220906192805.db
```

The newly created file at ~/.recon-ng/workspaces/test/ contains the exported 
SQLite database that can be further analysed within Jupyter notebook or some 
other environment. Note that we used the `back` command to exit the module 
sub-shell since some commands are not available there.

Now let us generate an HTML report. There's also a module for that.

```
[recon-ng][test] > modules load reporting/html
[recon-ng][test][html] > info

      Name: HTML Report Generator
    Author: Tim Tomes (@lanmaster53)
   Version: 1.0

Description:
  Creates an HTML report.

Options:
  Name      Current Value                                     Required  Description
  --------  -------------                                     --------  -----------
  CREATOR                                                     yes       use creator name in the report footer
  CUSTOMER                                                    yes       use customer name in the report header
  FILENAME  /Users/rl/.recon-ng/workspaces/test/results.html  yes       path and filename for report output
  SANITIZE  True                                              yes       mask sensitive data in the report

[recon-ng][test][html] > options set CREATOR rl1987
CREATOR => rl1987
[recon-ng][test][html] > options set CUSTOMER Shady Industries, Inc
CUSTOMER => Shady Industries, Inc
[recon-ng][test][html] > run
[*] Report generated at '/Users/rl/.recon-ng/workspaces/test/results.html'.
```

[Screenshot](/2022-09-06_19.33.29.png)

But what if we wanted to have a script to run everything we just did now in a reproducible
manner? Running recon-ng as a subprocess within some programming language and feeding the commands
through standard input could work, but is rather clunky. The good news is that we can create 
a text file with one command per line and use `-r` CLI option to run all the commands in batch
mode (don't forget the `exit` command at the end to make it finish without human intervention):

```
$ recon-ng -r script
```
