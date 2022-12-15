+++
author = "rl1987"
title = "Getting the data under version control with dolt"
date = "2022-12-15"
draft = true
tags = ["databases"]
+++

Many developers would agree that source code version control is a 
great thing that they would not imagine the modern software 
development without. What if it was applied for structured data
as well? Yes, technically it is possible to save SQLite file or SQL dump
into git repo, but that is rather clunky and outside the intended use
case of git. For proper version control, we would want row-level
diffing, ability to undo changes, group them into incremental chunks
(commits), have a way to review the proposed changes and many other nice
features that we have available in systems like git. 

Web scraper developers may find data version control to be of interest
for certain use cases. For example, one might be doing daily rescrapes
of product prices on eCommerce portal for the purpose of price intelligence.
Version-controlling the data provides an easy way to query the database
for changes between scraping jobs if we commit the data at the end of each
scraping job. This would enable automatically diffing the daily snapshots
and generating change report to be seen by the client paying for the 
scraping operation. 

[Dolt](https://github.com/dolthub/dolt) project is an up-and-coming DBMS 
that is meant to be a hybrid between MySQL and git.
It supports an SQL dialect that greatly overlaps with that of MySQL and
also provides a version control features that are based on the ones in git.

Dolt is a single-binary Go program that can be downloaded from Github
[tags page](https://github.com/dolthub/dolt/tags) or compiled from source code.
It is also available from Homebrew on macOS. Furthermore there are two official
Docker images on Docker Hub:

* [`dolthub/dolt`](https://hub.docker.com/r/dolthub/dolt) - for running dolt as CLI tool.
* [`dolthub/dolt-sql-server`](https://hub.docker.com/r/dolthub/dolt-sql-server) - for
running it in SQL server mode.

Dolt CLI is quite similar to git CLI:

```
$ dolt 
Valid commands for dolt are
                init - Create an empty Dolt data repository.
              status - Show the working tree status.
                 add - Add table changes to the list of staged table changes.
                diff - Diff a table.
               reset - Remove table changes from the list of staged table changes.
               clean - Remove untracked tables from working set.
              commit - Record changes to the repository.
                 sql - Run a SQL query against tables in repository.
          sql-server - Start a MySQL-compatible server.
          sql-client - Starts a built-in MySQL client.
                 log - Show commit logs.
              branch - Create, list, edit, delete branches.
            checkout - Checkout a branch or overwrite a table from HEAD.
               merge - Merge a branch.
           conflicts - Commands for viewing and resolving merge conflicts.
         cherry-pick - Apply the changes introduced by an existing commit.
              revert - Undo the changes introduced in a commit.
               clone - Clone from a remote data repository.
               fetch - Update the database from a remote data repository.
                pull - Fetch from a dolt remote data repository and merge.
                push - Push to a dolt remote.
              config - Dolt configuration.
              remote - Manage set of tracked repositories.
              backup - Manage a set of server backups.
               login - Login to a dolt remote host.
               creds - Commands for managing credentials.
                  ls - List tables in the working set.
              schema - Commands for showing and importing table schemas.
               table - Commands for copying, renaming, deleting, and exporting tables.
                 tag - Create, list, delete tags.
               blame - Show what revision and author last modified each row of a table.
         constraints - Commands for handling constraints.
             migrate - Executes a database migration to use the latest Dolt data format.
         read-tables - Fetch table(s) at a specific commit into a new dolt repo
                  gc - Cleans up unreferenced data from the repository.
       filter-branch - Edits the commit history using the provided query.
          merge-base - Find the common ancestor of two commits.
             version - Displays the current Dolt cli version.
                dump - Export all tables in the working set into a file.
                docs - Commands for working with Dolt documents.
```

We have commands for adding changes to staging area, commiting them to change history,
making branches, communicating with remote servers, resolving merge conflicts and so on.
Note, however, that not every VCS feature supported by git is supported by dolt. 
Furthemore, we see some commands related to DB functionality such as `sql`, 
`schema` and `dump`. Lastly, we have `docs` command that provides a little of
functionality for version-controlling your database documentation, such as README
file and such.

Dolt stores all the database contents in a single directory per database, which makes
it easy to backup and migrate between servers.

SQL dialect of Dolt is largely the same as the one used in MySQL with two notable 
differences. First, not all advanced features of MySQL are supported at this point
(see the list of [supported statements](https://docs.dolthub.com/sql-reference/sql-support/supported-statements)).
Second, Dolt introduces some more SQL statements that are related to version
control aspect (see [Version control](https://docs.dolthub.com/sql-reference/version-control)
section of the official documentation).

To run Dolt in SQL server mode one could run `dolt sql-server` command. This 
launches a network server that talks the MySQL protocol and can be used
with a MySQL client programs or libraries (e.g. mysql-connector). 
Furthermore, Dolt includes a simple SQL client that can be launched by 
running `dolt sql-client`. There are also some official Python client libraries for Dolt:

* [DoltPy](https://github.com/dolthub/doltpy) implements Dolt SQL client
* [doltcli](https://github.com/dolthub/doltcli) is a wrapper around dolt CLI tool
to run queries locally without running Dolt as server.

For git users, there's Github for community and collaboration. 
[DoltHub](https://www.dolthub.com/) is a company and portal that not only
develops dolt, but also lets you publically host your databases. If you don't
want to host it publically there are two options:

* [DoltLab](http://doltlab.dolthub.com/) - a self-hostable, more private solution
similar to GitLab. DoltLab is to dolt what GitLab is to Git.
* [Hosted Dolt](https://hosted.doltdb.com) - an equivalent of AWS RDS for
Dolt server. You get a dolt server that is provisioned and maintained for you,
no DBA needed.

DoltHub Inc. is also running public data bounties that entail gathering open 
data by scraping, wrangling and importing it into structured database. Participants
are paid based on how much of the data they submitted via pull requests was accepted.
This can be an opportunity to make some money if you're a web scraper developer.
