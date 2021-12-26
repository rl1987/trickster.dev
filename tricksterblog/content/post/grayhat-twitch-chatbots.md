+++
author = "rl1987"
title = "Grayhat Twitch Chatbots"
date = "2021-12-31"
draft = true
tags = ["python", "automation"]
+++

Twitch is a popular video streaming platform platform originally developed for gamers, but now acquired by Amazon expanding beyond gaming community.
It enables viewers to use chat rooms associated with video streams to communicate amongst each other and with the streamer. Chat bots for these
chatrooms can be used for legitimate uses cases such as moderations, polls, ranking boards and so on. Twitch is allowing such usage, but requires
passing a [verification process](https://dev.twitch.tv/docs/irc/guide#verified-bots) for chat bot software to be used in production at scale.
On more black hat side of things, they have been used to launch harassment campaigns (hate raids) against streamers and content creators. 
We are interested in gray hat automation here and will be looking into developing a chat bot that connects to one or more channels as a regular
user. This can be used for growth hacking purposes if one is trying to promote an offer that is of interest to gaming community.

Little known fact is that good old Internet Relay Chat protocol for the chat functionality, but wraps the IRC connections in WebSockets to
make it compatible with web browser. Twitch implementation of IRC is mostly compliant to [RFC1459](https://datatracker.ietf.org/doc/html/rfc1459.html)
with some differences regarding authentication - see [Chatbots and IRC Guide](https://dev.twitch.tv/docs/irc/guide) at Twitch developer portal.
In fact, it is possible to use Irssi or other IRC client with Twitch. 

To see IRC messages being sent and received on Twitch chat connection, one can simply check the Network tab via Chrome DevTools and filter by 
WebSocket (choose WS from the options at the top).

TODO: add screenshot

The white hat approach would be to register an app at Twitch and implement OAuth or OpenID Connect flow as described in 
[Authentication section](https://dev.twitch.tv/docs/authentication) of Twitch developer documentation. We are going to skip this
as we want our bots to appear as regular users.

To login to Twitch as a regular user would, be need to use Chrome DevTools to explore the login flow so that we could reproduce it
programmatically. When trying to login to Twitch, we find that POST request is being made to `https://passport.twitch.tv/login` with
JSON payload containing single dictionary with following key-value pairs:

* `client_id` seems to be an internal ID of API client. Reuse original value.
* `password` - plaintext password to the account
* `undelete_user` is `false`.
* `username` - user name of the account.

There are some cookies that we have to set as well. We can get most of them by simply loading some regular page and saving the cookies
we receive with the response. However, we have to set `api_token` cookie to the value that we see in the API request from the frontend.

However this request may fail with response code 400. If this happens, we either need to solve a Captcha or send another request
to submit verification code that was emailed to the user. The former case is relatively rare and will not be covered by this post.
The latter is relatively common and can be addressed as follows.

TODO: add screenshot

If Twitch asks for verification code, we need to send another request to the same. JSON dictionary in the payload has to be
updated with the following:

* `captcha` key points to dictionary with single key-value pair:
  * `proof` is value for `captcha_proof` key from response to previous request.
* `twitchguard_code` is the code that was sent through email.

Once we submit this payload quickly enough (there's some time out on Twitch side that will cause it to ask for another confirmation
if we're being too slow), we receive a response containing the authentication token at key `access_token`. Furthermore, we also
receive some new cookies that we have too keep for further communications with Twitch.


WRITEME: joining the channel via websocket

TODO: develop a complete script that implements a basic chatbot

