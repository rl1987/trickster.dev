+++
author = "rl1987"
title = "GraphQL for scraping and automation"
date = "2022-01-31"
draft = true
tags = ["scraping", "automation", "graphql"]
+++

Most developers are familiar with the concept of REST API and it's use to implement communications between
software systems. At it's core, REST APIs expose data model entities through endpoints - URL path prefixes
and allow the client software to perform operations by sending a corresponding HTTP requests - GET requests
fetches the resource, POST request creates the resource, DELETE request deletes it and so on.

However, it was found that REST APIs have the following disadvantages:

* REST is an architectural principle and not a detailed specification. It leaves a lot to interpretation and
one has to fill a lot of gaps when designing and implementing REST APIs. There is no pre-defined way to 
perform schema validation.
* Lack of flexibility when generating requests can lead to both overfetching and underfetching the data. 
Overfetching happens when client software needs a small subset of data that the server normally returns.
Underfetching happens when client must use multiple requests to gather all the data it needs from multiple
API endpoints. Both are wasteful in terms of resource utilization.

To solve these problems, Facebook developed GraphQL - a query language that lets data model to be formally
expressed in graph-theorethical way and started GraphQL Foundation to further oversee it's development and promote
the adotion. Unlike REST, GraphQL has a formal [specification](https://spec.graphql.org/June2018/)
that describes it unambiguously in great detail. Furthermore, GraphQL lets developers to fetch or modify the exact 
data they need in a single request thus avoiding performance issues. If REST API operations are
equavalent to running SQL queries that touch a single table of relational database at a time then GraphQL does not
have that limitation. Yet another advantage of GraphQL is schema validation being performed automatically
on the server for each query.

When working with scraping and automation, it is not uncommon to come across GraphQL APIs being used to
implement communications between client and server parts of various systems. Shopify, Product Hunt, GOAT
are prominent examples of major companies that use GraphQL.


