+++
author = "rl1987"
title = "Using proxies for web scraping and automation"
date = "2022-01-31"
tags = ["automation", "scraping", "proxies"]
+++

When it comes to scraping and automation operations, it might be important to control where remote systems see the traffic
coming from to evade rate-limiting, captchas and IP bans. This is what we need to use proxies for.
Let us talk about individual proxy servers and proxy pools.

Proxy server is server somewhere in the network that acts as middleman for network communications. One way this can
work is connection-level proxying via SOCKS protocol. The client would make a connection to SOCKS server and ask it to
make another connection to the real destination address. Once this is done, the remote server sees the second connection
coming from proxy IP address and the resulting two-legged connection can be used to make requests to the server, thus hiding
their true source. Another way is HTTP request forwarding. HTTP proxy would listen to incoming requests and forward them to
their true destination. Third way is a hybrid approach of client establishing TCP connection to proxy server, sending HTTP
CONNECT request to make it connect to remote destination server and then using it for further HTTP-based communication with the
true destination server. This is known as HTTP tunneling.

Proxy pool is a geographically distributed network of proxy servers that accept incoming traffic at single IP or DNS address,
and spread out the outgoing traffic through large number of exit IP addresses.

There are the following main categories of proxies.

* Datacenter proxies that reroute traffic through datacenter and public cloud systems. Good enough to evade simple rate-limiting
and IP-based blocking, but insufficient when dealing with more advanced countermeasures. However they are very cheap.
* ISP proxies from providers that have deals with ISPs and can use IP addresses from residential ranges. More expensive 
and more capable to evade blocking. 
* Residential proxies reroute traffic through homes of real people. One may ask: how is this possible? The answer is that
certain companies are either paying home users for their bandwidth or incentivise traffic sharing through things like free
VPN service. On a darker end of spectrum, users of some freeware apps may be sharing their traffic unknowingly or even be
infected with malware as was the case with [Glupteba](https://threatpost.com/google-glupteba-botnet-lawsuit/176826/) botnet.
However, note that not all proxies marketed as residential are truly residential. Some are actually ISP proxies. Depending
on your proxy provider, you may need to go through more complicated verification procedure to get access.
* Most expensive are mobile proxies that have exit IPs from mobile networks. This does not necessarily mean that traffic is
coming from real phone of real user. It might be solution similar to [Proxidize](https://proxidize.com/) that entails some
setup with cellular modems and SIM cards. Mobile proxies provide significant blocking evasion capacity and are used for social media
automation in a post-Cambridge Analytica world.
* Lastly, there's advanced proxies like [Bright Data Web Unlocker](https://brightdata.com/products/web-unlocker) and [Zyte
Smart Proxy Manager](https://www.zyte.com/smart-proxy-manager/) (formerly known as Crawlera). These proxy services implement
proprietary advanced blocking evasion techniques and can be used to scrape sites protected by anti-botting solutions like
PerimeterX. However there is one drawback - for the purpose of blocking evasion they might overtake cookie management, which
means you may not be able to do things that require you to set up session with cookies (e.g. to scrape behind login).

You may also have heard the term "dedicated proxy". Dedicated proxy is a single proxy server that proxy provider rents to one
customer at a time. By default, proxy pools provide what is called rotating proxies - a network of proxies that load balance
the outgoing traffic by rotating exit IPs for you. Sometimes they provide a way to lock into a single exit IP for a limited 
duration of session - this is called "sticky sessions".

You may have seen some sites with long list of free proxy addresses. These are no good for serious web scraping operations
as many of them do not even work and the ones that work are unreliable. Furthermore, they may betray the real source IP address
through HTTP headers.

Some proxy providers you may want to check out are:

* [Bright Data](https://brightdata.com/)
* [OxyLabs](https://oxylabs.io/)
* [PacketStream](https://packetstream.io/)
* [ScraperAPI](https://www.scraperapi.com/)
* [Geosurf](https://www.geosurf.com/)
* [Oculus Proxies](https://oculusproxies.com/index)
* [The Social Proxy](https://thesocialproxy.com/)

There's also many more. Due your research to find the best option for your budget and use case.

How would we use proxies in our code? Bright Data provides the following Python snippet for simple use case of their proxy service.

```python
#!/usr/bin/env python
print('If you get error "ImportError: No module named \'six\'" install six:\n'+\
    '$ sudo pip install six');
print('To enable your free eval account and get CUSTOMER, YOURZONE and ' + \
    'YOURPASS, please contact sales@brightdata.com')
import sys
if sys.version_info[0]==2:
    import six
    from six.moves.urllib import request
    opener = request.build_opener(
        request.ProxyHandler(
            {'http': 'http://[REDACTED]:[REDACTED]@zproxy.lum-superproxy.io:22225',
            'https': 'http://[REDACTED]:[REDACTED]@zproxy.lum-superproxy.io:22225'}))
    print(opener.open('http://lumtest.com/myip.json').read())
if sys.version_info[0]==3:
    import urllib.request
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler(
            {'http': 'http://[REDACTED]:[REDACTED]@zproxy.lum-superproxy.io:22225',
            'https': 'http://[REDACTED]:[REDACTED]@zproxy.lum-superproxy.io:22225'}))
    print(opener.open('http://lumtest.com/myip.json').read())
```

If you are using requests module for making HTTP requests (as you should) you can simply copy the proxy URL from the snippet
Bright Data provides and either set `HTTPS_PROXY` environment variable with that, or create a proxies dictionary and use it for
requests like this:

```python
proxies = {
    'http': PROXY_URL,
    'https': PROXY_URL
}

resp = requests.get(url, proxies=proxies)
```

See the [official documentation](https://2.python-requests.org/en/master/user/advanced/#proxies) to read more about this.

There is one more snippet on Bright Data dashboard that is of interest to us - the "High-perf parallel requests" example:

```python
#!/usr/bin/env python
print('If you get error "ImportError: No module named \'six\'" install six:\n'+\
    '$ sudo pip install six');
print('If you get error "ImportError: No module named \'eventlet\'" install' +\
    'eventlet:\n$ sudo pip install eventlet');
print('To enable your free eval account and get CUSTOMER, YOURZONE and ' + \
    'YOURPASS, please contact sales@brightdata.com')
import sys
import eventlet
if sys.version_info[0]==2:
    import six
    from six.moves.urllib import request
if sys.version_info[0]==3:
    from eventlet.green.urllib import request
import random
import socket

super_proxy = socket.gethostbyname('zproxy.lum-superproxy.io')

class SingleSessionRetriever:

    url = "http://%s-session-%s:%s@"+super_proxy+":%d"
    port = 22225

    def __init__(self, username, password, requests_limit, failures_limit):
        self._username = username
        self._password = password
        self._requests_limit = requests_limit
        self._failures_limit = failures_limit
        self._reset_session()

    def _reset_session(self):
        session_id = random.random()
        proxy = SingleSessionRetriever.url % (self._username, session_id, self._password,
                                              SingleSessionRetriever.port)
        proxy_handler = request.ProxyHandler({'http': proxy, 'https': proxy})
        self._opener = request.build_opener(proxy_handler)
        self._requests = 0
        self._failures = 0

    def retrieve(self, url, timeout):
        while True:
            if self._requests == self._requests_limit:
                self._reset_session()
            self._requests += 1
            try:
                timer = eventlet.Timeout(timeout)
                result = self._opener.open(url).read()
                timer.cancel()
                return result
            except:
                timer.cancel()
                self._failures += 1
                if self._failures == self._failures_limit:
                    self._reset_session()


class MultiSessionRetriever:

    def __init__(self, username, password, session_requests_limit, session_failures_limit):
        self._username = username
        self._password = password
        self._sessions_stack = []
        self._session_requests_limit = session_requests_limit
        self._session_failures_limit = session_failures_limit

    def retrieve(self, urls, timeout, parallel_sessions_limit, callback):
        pool = eventlet.GreenPool(parallel_sessions_limit)
        for url, body in pool.imap(lambda url: self._retrieve_single(url, timeout), urls):
            callback(url, body)

    def _retrieve_single(self, url, timeout):
        if self._sessions_stack:
            session = self._sessions_stack.pop()
        else:
            session = SingleSessionRetriever(self._username, self._password,
                                             self._session_requests_limit, self._session_failures_limit)
        body = session.retrieve(url, timeout)
        self._sessions_stack.append(session)
        return url, body

def output(url, body):
    print(body)

n_total_req = 100
req_timeout = 10
n_parallel_exit_nodes = 10
switch_ip_every_n_req = 10
max_failures = 2

MultiSessionRetriever('[REDACTED]', '[REDACTED]', switch_ip_every_n_req, max_failures).retrieve(
    ["http://lumtest.com/myip.json"] * n_total_req, req_timeout, n_parallel_exit_nodes, output)
```

This uses [eventlet](https://eventlet.net/) module to implement concurrent networking, which is highly useful
for web scraping, as most the time web scraping code spends goes into waiting for HTTP responses to come from the servers.
Running multiple requests concurrently can speed up web scraping job by orders of magnitude, as long as we don't run into
rate-limiting and other countermeasures against scraping that might be implemented by website operators. Launching concurrent
requests through the proxy pool enables us to benefit from performance improvements that come from concurrent requests while
still being able to evade blocking.

Furthermore, I would like to direct attention to `SingleSessionRetriever._reset_session()` method. We see that a random session
ID value is being generated and appended to proxy user name, which is Bright Data's way to let us have sticky sessions. However, 
in this case it is also being used to force exit IP randomisation every 10 requests. That might be necessary to avoid getting
rate-limited or other forms of blocking when scraping some sites.


