+++
author = "rl1987"
title = "HTTPX: modern Python module for doing HTTP(S) requests"
date = "2022-09-17"
draft = true
tags = ["python", "scraping", "automation"]
+++

Python [requests](https://requests.readthedocs.io/en/latest/) module is a
well established open source library for doing HTTP requests that is widely
used in web scraping and other fields. However it has some limitations.
At the time of writing, requests module only supports HTTP/1.1 yet
significant fraction of sites are supporting more modern, faster HTTP/2 
protocol. Furthermore, there is no support for asynchronous communication
in requests module.

[HTTPX](https://www.python-httpx.org/) is a newer, more modern Python
module that addresses some of the limitations of requests module (not to be 
confused with [another httpx](https://github.com/projectdiscovery/httpx)
that is CLI tool for probing HTTP servers). It can be installed as `httpx`
through PIP. Furthermore, one can install the following optional dependencies:

* `h2` for HTTP/2 support (through `httpx[http2]`)
* `socksio` for SOCKS proxy support (through `httpx[socks]`)
* `click` for optional CLI tool (through `httpx[cli]`)
* `rich` for making the optional CLI tool prettier
* `brotli` or `brotlicffi` for supporting Cloudflare's Brotli compression (through `httpx[brotli]`)

HTTPX is largely, but not entirely a drop-in replacement for the aforementioned
requests module. Let us launch Python REPL and make a simple HTTPS request.

```
$ python3
Python 3.10.6 (main, Aug 30 2022, 04:58:14) [Clang 13.1.6 (clang-1316.0.21.2.5)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import httpx
>>> resp = httpx.get("https://api.github.com/users/facebook-github-bot/events/public")
>>> resp
<Response [200 OK]>
>>> resp.status_code
200
>>> resp.text[:100]
'[{"id":"24020632984","type":"IssueCommentEvent","actor":{"id":6422482,"login":"facebook-github-bot",'
>>> type(resp.json())
<class 'list'>
>>> resp.json()[0]
{'id': '24020632984', 'type': 'IssueCommentEvent', 'actor': {'id': 6422482, 'login': 'facebook-github-bot', 'display_login': 'facebook-github-bot', 'gravatar_id': '', 'url': 'https://api.github.com/users/facebook-github-bot', 'avatar_url': 'https://avatars.githubusercontent.com/u/6422482?'}, 'repo': {'id': 392055467, 'name': 'facebookresearch/fbpcs', 'url': 'https://api.github.com/repos/facebookresearch/fbpcs'}, 'payload': {'action': 'created', 'issue': {'url': 'https://api.github.com/repos/facebookresearch/fbpcs/issues/432', 'repository_url': 'https://api.github.com/repos/facebookresearch/fbpcs', 'labels_url': 'https://api.github.com/repos/facebookresearch/fbpcs/issues/432/labels{/name}', 'comments_url': 'https://api.github.com/repos/facebookresearch/fbpcs/issues/432/comments', 'events_url': 'https://api.github.com/repos/facebookresearch/fbpcs/issues/432/events', 'html_url': 'https://github.com/facebookresearch/fbpcs/pull/432', 'id': 1070015172, 'node_id': 'PR_kwDOF15Kq84vVQRm', 'number': 432, 'title': 'update graphapi version', 'user': {'login': 'benliugithub', 'id': 90293689, 'node_id': 'MDQ6VXNlcjkwMjkzNjg5', 'avatar_url': 'https://avatars.githubusercontent.com/u/90293689?v=4', 'gravatar_id': '', 'url': 'https://api.github.com/users/benliugithub', 'html_url': 'https://github.com/benliugithub', 'followers_url': 'https://api.github.com/users/benliugithub/followers', 'following_url': 'https://api.github.com/users/benliugithub/following{/other_user}', 'gists_url': 'https://api.github.com/users/benliugithub/gists{/gist_id}', 'starred_url': 'https://api.github.com/users/benliugithub/starred{/owner}{/repo}', 'subscriptions_url': 'https://api.github.com/users/benliugithub/subscriptions', 'organizations_url': 'https://api.github.com/users/benliugithub/orgs', 'repos_url': 'https://api.github.com/users/benliugithub/repos', 'events_url': 'https://api.github.com/users/benliugithub/events{/privacy}', 'received_events_url': 'https://api.github.com/users/benliugithub/received_events', 'type': 'User', 'site_admin': False}, 'labels': [{'id': 3223376167, 'node_id': 'MDU6TGFiZWwzMjIzMzc2MTY3', 'url': 'https://api.github.com/repos/facebookresearch/fbpcs/labels/CLA%20Signed', 'name': 'CLA Signed', 'color': '009900', 'default': False, 'description': 'This label is managed by the Facebook bot. Authors need to sign the CLA before a PR can be reviewed.'}, {'id': 3251191745, 'node_id': 'MDU6TGFiZWwzMjUxMTkxNzQ1', 'url': 'https://api.github.com/repos/facebookresearch/fbpcs/labels/fb-exported', 'name': 'fb-exported', 'color': 'ededed', 'default': False, 'description': None}], 'state': 'open', 'locked': False, 'assignee': None, 'assignees': [], 'milestone': None, 'comments': 1, 'created_at': '2021-12-02T21:54:32Z', 'updated_at': '2022-09-15T07:20:13Z', 'closed_at': None, 'author_association': 'NONE', 'active_lock_reason': None, 'draft': False, 'pull_request': {'url': 'https://api.github.com/repos/facebookresearch/fbpcs/pulls/432', 'html_url': 'https://github.com/facebookresearch/fbpcs/pull/432', 'diff_url': 'https://github.com/facebookresearch/fbpcs/pull/432.diff', 'patch_url': 'https://github.com/facebookresearch/fbpcs/pull/432.patch', 'merged_at': None}, 'body': 'Summary: As title\n\nReviewed By: leegross\n\nDifferential Revision: D32811061\n\n', 'reactions': {'url': 'https://api.github.com/repos/facebookresearch/fbpcs/issues/432/reactions', 'total_count': 0, '+1': 0, '-1': 0, 'laugh': 0, 'hooray': 0, 'confused': 0, 'heart': 0, 'rocket': 0, 'eyes': 0}, 'timeline_url': 'https://api.github.com/repos/facebookresearch/fbpcs/issues/432/timeline', 'performed_via_github_app': None, 'state_reason': None}, 'comment': {'url': 'https://api.github.com/repos/facebookresearch/fbpcs/issues/comments/1247684175', 'html_url': 'https://github.com/facebookresearch/fbpcs/pull/432#issuecomment-1247684175', 'issue_url': 'https://api.github.com/repos/facebookresearch/fbpcs/issues/432', 'id': 1247684175, 'node_id': 'IC_kwDOF15Kq85KXiZP', 'user': {'login': 'facebook-github-bot', 'id': 6422482, 'node_id': 'MDQ6VXNlcjY0MjI0ODI=', 'avatar_url': 'https://avatars.githubusercontent.com/u/6422482?v=4', 'gravatar_id': '', 'url': 'https://api.github.com/users/facebook-github-bot', 'html_url': 'https://github.com/facebook-github-bot', 'followers_url': 'https://api.github.com/users/facebook-github-bot/followers', 'following_url': 'https://api.github.com/users/facebook-github-bot/following{/other_user}', 'gists_url': 'https://api.github.com/users/facebook-github-bot/gists{/gist_id}', 'starred_url': 'https://api.github.com/users/facebook-github-bot/starred{/owner}{/repo}', 'subscriptions_url': 'https://api.github.com/users/facebook-github-bot/subscriptions', 'organizations_url': 'https://api.github.com/users/facebook-github-bot/orgs', 'repos_url': 'https://api.github.com/users/facebook-github-bot/repos', 'events_url': 'https://api.github.com/users/facebook-github-bot/events{/privacy}', 'received_events_url': 'https://api.github.com/users/facebook-github-bot/received_events', 'type': 'User', 'site_admin': False}, 'created_at': '2022-09-15T07:20:13Z', 'updated_at': '2022-09-15T07:20:13Z', 'author_association': 'CONTRIBUTOR', 'body': 'Hi @benliugithub! \n\nThank you for your pull request. \n\nWe **require** contributors to sign our **Contributor License Agreement**, and yours needs attention.\n\nYou currently have a record in our system, but the CLA is no longer valid, and will need to be **resubmitted**.\n\n# Process\n\nIn order for us to review and merge your suggested changes, please sign at <https://code.facebook.com/cla>. **If you are contributing on behalf of someone else (eg your employer)**, the individual CLA may not be sufficient and your employer may need to sign the corporate CLA.\n\nOnce the CLA is signed, our tooling will perform checks and validations. Afterwards, the **pull request will be tagged** with `CLA signed`. The tagging process may take up to 1 hour after signing. Please give it that time before contacting us about it.\n\nIf you have received this in error or have any questions, please contact us at [cla@fb.com](mailto:cla@fb.com?subject=CLA%20for%20facebookresearch%2Ffbpcs%20%23432). Thanks!', 'reactions': {'url': 'https://api.github.com/repos/facebookresearch/fbpcs/issues/comments/1247684175/reactions', 'total_count': 0, '+1': 0, '-1': 0, 'laugh': 0, 'hooray': 0, 'confused': 0, 'heart': 0, 'rocket': 0, 'eyes': 0}, 'performed_via_github_app': None}}, 'public': True, 'created_at': '2022-09-15T07:20:14Z', 'org': {'id': 16943930, 'login': 'facebookresearch', 'gravatar_id': '', 'url': 'https://api.github.com/orgs/facebookresearch', 'avatar_url': 'https://avatars.githubusercontent.com/u/16943930?'}}
```

This was HTTP/1.1 request. But what if we wanted to launch a HTTP/2 request?
Assuming `httpx[http2]` is installed, we would need instantiate a client object
with `http2` keyword argument set to true:

```
>>> client = httpx.Client(http2=True)
>>> client
<httpx.Client object at 0x105f3a2c0>
>>> resp = client.get("https://api.github.com/users/facebook-github-bot/events/public")
>>> resp
<Response [200 OK]>
>>> resp.text[:100]
'[{"id":"24020972057","type":"PullRequestEvent","actor":{"id":6422482,"login":"facebook-github-bot","'
>>> resp.http_version
'HTTP/2'
```



The client object in HTTPX is largely equivalent to `requests.Session`: it can manage cookies
between requests, reuse headers, proxy URLs and other settings. Furthermore, HTTPX client implements HTTP
connection pooling for improved performance. This entails refraining from closing TCP connections
to remote servers after getting response and keeping them available to save time when new request
is available. The client object can be used as context manager, but if we wanted to explicitly
close all connection in the pool we could do so by calling `close()` method.

If we want to benefit from async I/O we can use `httpx.AsyncClient` instead of `httpx.Client`:

```
$ python3 -m asyncio
asyncio REPL 3.10.6 (main, Aug 30 2022, 04:58:14) [Clang 13.1.6 (clang-1316.0.21.2.5)] on darwin
Use "await" directly instead of "asyncio.run()".
Type "help", "copyright", "credits" or "license" for more information.
>>> import asyncio
>>> import httpx
>>> async with httpx.AsyncClient() as client:
...     resp = await client.get("https://instagram.com")
... 
>>> resp
<Response [301 Moved Permanently]>
```

If you have installed the optional `httpx[cli]` submodule, you can use the CLI tool that is
developed with the library:

```
$ httpx --download fb_bot.json https://api.github.com/users/facebook-github-bot/events/public
HTTP/1.1 200 OK
Server: GitHub.com
Date: Thu, 15 Sep 2022 07:53:21 GMT
Content-Type: application/json; charset=utf-8
Cache-Control: public, max-age=60, s-maxage=60
Vary: Accept, Accept-Encoding, Accept, X-Requested-With
ETag: W/"0d377aecaac2a62f7662fc84bfb6ca33a1e6372d14da1fa4f89a3a39f02e8191"
Last-Modified: Thu, 15 Sep 2022 07:44:01 GMT
X-Poll-Interval: 60
X-GitHub-Media-Type: github.v3; format=json
Link: <https://api.github.com/user/6422482/events/public?page=2>; rel="next", <https://api.github.com/user/6422482/events/public?page=8>; rel="last"
Access-Control-Expose-Headers: ETag, Link, Location, Retry-After, X-GitHub-OTP, X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Used, X-RateLimit-Resource, X-RateLimit-Reset, X-OAuth-Scopes, 
X-Accepted-OAuth-Scopes, X-Poll-Interval, X-GitHub-Media-Type, X-GitHub-SSO, X-GitHub-Request-Id, Deprecation, Sunset
Access-Control-Allow-Origin: *
Strict-Transport-Security: max-age=31536000; includeSubdomains; preload
X-Frame-Options: deny
X-Content-Type-Options: nosniff
X-XSS-Protection: 0
Referrer-Policy: origin-when-cross-origin, strict-origin-when-cross-origin
Content-Security-Policy: default-src 'none'
Content-Encoding: gzip
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 52
X-RateLimit-Reset: 1663229406
X-RateLimit-Resource: core
X-RateLimit-Used: 8
Accept-Ranges: bytes
Transfer-Encoding: chunked
X-GitHub-Request-Id: EA77:1A4B:39239D:3B3337:6322D9F0


Downloading fb_bot.json   0% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 16,286/0 bytes ?
$ file fb_bot.json 
fb_bot.json: JSON data
```

HTTPX heeds the following environment variables:

* `HTTPX_LOG_LEVEL` - enables extra logging for debugging purposes (can be `debug` or `trace`)
* `SSLKEYLOGFILE` - path for saving TLS handshake secrets, so that TLS connections can
be [decrypted in Wireshark](../decrypting-your-own-https-traffic-with-wireshark).
* `HTTP_PROXY` and `HTTPS_PROXY` - proxy URLs to be used for HTTP and HTTPS requests.
* `ALL_PROXY` - proxy URL to be used for all requests.
* `NO_PROXY` - comma-separated list of hostnames and URLs that should be accessed without
proxying.
* `NETRC` - a path to a [.netrc](https://everything.curl.dev/usingcurl/netrc) file.
* `SSL_CERT_FILE` - path to custom CA certificate (.crt file). This may be useful when
working with proxies that intercept TLS connections.
* `SSL_CERT_DIR` - X.509 certificate directory path. This directory is expected to follow 
the OpenSSL layout.

