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
On more black hat side of things, bots have been used to launch harassment campaigns (hate raids) against streamers and content creators. 
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

If Twitch asks for verification code, we need to send another request to the same API endpoint. JSON dictionary in the payload
has to be updated with the following:

* `captcha` key points to dictionary with single key-value pair:
  * `proof` is value for `captcha_proof` key from response to previous request.
* `twitchguard_code` is the code that was sent through email.

Once we submit this payload quickly enough (there's some time out on Twitch side that will cause it to ask for another confirmation
if we're being too slow), we receive a response with JSON dictionary containing the authentication token at key `access_token`.
Furthermore, we also receive some new cookies that we have too keep for further communications with Twitch.

Now we need to join a channel. To explore the API dance, I encourage you to join a live stream on Twitch and see what API messages
are appearing in Network tab of Chrome DevTools (switch to "Fetch/XHR" to see only the stuff we're interested in here).
You will see a lot of API calls to `https://gql.twitch.tv/gql`, most of which are related to things other than chat (video stream
playback, etc.). To be able to post chat messages to most channels, one has to follow a channel first, which is accomplished by
API call with the following payload:

```json
[
    {
        "operationName": "FollowButton_FollowUser",
        "variables": {
            "input": {
                "disableNotifications": false,
                "targetID": "24070690"
            }
        },
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "800e7346bdf7e5278a3c1d3f21b2b56e2639928f86815677a7126b093b2fdd08"
            }
        }
    },
    {
        "operationName": "AvailableEmotesForChannel",
        "variables": {
            "channelID": "24070690",
            "withOwner": true
        },
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "b9ce64d02e26c6fe9adbfb3991284224498b295542f9c5a51eacd3610e659cfb"
            }
        }
    }
]
```

In this example, number `24070690` is unique numeric ID for the channel we want to join. Yet it does not appear anywhere in
Twitch page URL, which in this case is https://www.twitch.tv/pedguin. How does the frontend code get this number?

Let's go back to the first API call that is made when stream page is being loaded. It has the following payload:

```json
{
    "operationName": "PlaybackAccessToken_Template",
    "query": "query PlaybackAccessToken_Template($login: String!, $isLive: Boolean!, $vodID: ID!, $isVod: Boolean!, $playerType: String!) {  streamPlaybackAccessToken(channelName: $login, params: {platform: \"web\", playerBackend: \"mediaplayer\", playerType: $playerType}) @include(if: $isLive) {    value    signature    __typename  }  videoPlaybackAccessToken(id: $vodID, params: {platform: \"web\", playerBackend: \"mediaplayer\", playerType: $playerType}) @include(if: $isVod) {    value    signature    __typename  }}",
    "variables": {
        "isLive": true,
        "login": "pedguin",
        "isVod": false,
        "vodID": "",
        "playerType": "site"
    }
}
```

The response to this GraphQL query is the following:

```json
{
    "data": {
        "streamPlaybackAccessToken": {
            "value": "{\"adblock\":false,\"authorization\":{\"forbidden\":false,\"reason\":\"\"},\"blackout_enabled\":false,\"channel\":\"pedguin\",\"channel_id\":24070690,\"chansub\":{\"restricted_bitrates\":[],\"view_until\":1924905600},\"ci_gb\":false,\"geoblock_reason\":\"\",\"device_id\":\"twitch-web-wall-mason\",\"expires\":1640538149,\"extended_history_allowed\":false,\"game\":\"\",\"hide_ads\":false,\"https_required\":true,\"mature\":false,\"partner\":false,\"platform\":\"web\",\"player_type\":\"site\",\"private\":{\"allowed_to_view\":true},\"privileged\":false,\"role\":\"\",\"server_ads\":true,\"show_ads\":true,\"subscriber\":false,\"turbo\":false,\"user_id\":[REDACTED],\"user_ip\":\"[REDACTED]\",\"version\":2}",
            "signature": "4992225a5ea06184d4c6c6c1187a77de55f1b7e8",
            "__typename": "PlaybackAccessToken"
        }
    },
    "extensions": {
        "durationMilliseconds": 68,
        "operationName": "PlaybackAccessToken_Template",
        "requestID": "01FQVSYG7KR0K7850XKBV27C1A"
    }
}
```

We find the numeric channel ID in the nested JSON string and can extract it.

Once we have followed a channel, we need to make a WebSocket connection to `wss://irc-ws.chat.twitch.tv/` and send the following 
IRC messages:

1. `CAP REQ :twitch.tv/tags twitch.tv/commands` - this enables Twitch specific IRC commands.
2. `PASS` message with `oauth:` prepended to auth token we received when creating a session with username and password.
3. `NICK` message with your username.
4. `USER` message with your username. Does not seem to be strictly necessary, but Twitch frontend sends this and we will send it as well.
5. `JOIN` message with channel name that you get from stream URL. For example if stream URL is `https://twitch.tv/foo`, then this ould be `JOIN #foo`.

After sending all these messages, we will be receiving and sending messages in IRC wire format. See RFC1459 for more details.

TODO: develop a complete script that implements a basic chatbot

