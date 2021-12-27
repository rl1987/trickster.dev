+++
author = "rl1987"
title = "Grayhat Twitch Chatbots"
date = "2021-12-31"
draft = true
tags = ["python", "automation"]
+++

Twitch is a popular video streaming platform originally developed for gamers, but now expanding beyond gaming community.
It enables viewers to use chat rooms associated with video streams to communicate amongst each other and with the streamer. Chatbots for these
chatrooms can be used for legitimate uses cases such as moderations, polls, ranking boards, and so on. Twitch is allowing such usage but requires
passing a [verification process](https://dev.twitch.tv/docs/irc/guide#verified-bots) for chatbot software to be used in production at scale.
On a more black hat side of things, bots have been used to launch harassment campaigns (hate raids) against streamers and content creators. 
We are interested in gray hat automation here and will be looking into developing a chat bot that connects to one or more channels as a regular
user. This can be used for growth hacking purposes if one is trying to promote an offer that is of interest to gaming community.

Little known fact is that Twitch uses the good old Internet Relay Chat protocol for the chat functionality, but wraps the IRC connections in WebSockets to
make it compatible with web browser. Twitch implementation of IRC is mostly compliant to [RFC1459](https://datatracker.ietf.org/doc/html/rfc1459.html)
with some differences regarding authentication - see [Chatbots and IRC Guide](https://dev.twitch.tv/docs/irc/guide) at Twitch developer portal.
In fact, it is possible to use Irssi or other IRC client with Twitch. 

To see IRC messages being sent and received on Twitch chat connection, one can simply check the Network tab via Chrome DevTools and filter by 
WebSocket (choose WS from the options at the top).

[Screenshot](/2021-12-26_16.12.44.png)

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

[Screenshot](/2021-12-26_17.36.06.png)

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
API call with the following payload (reformatted for readability):

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

The response to this GraphQL request has the following payload:

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
5. `JOIN` message with channel name that you get from stream URL. For example if stream URL is `https://twitch.tv/foo`, then this would be `JOIN #foo`.

After sending all these messages, we will be receiving and sending messages in IRC wire format. See RFC1459 and related RFCs for 
more details.

The following code implement all the API flows we have discussed so far and provides a simple chat bot functionality: whenever it
detects a string `!test`, it responds with hardcoded message. For the WebSocket part, we use `websocket_client` module from PIP.

```python
#!/usr/bin/python3

import logging
import json
import uuid

import requests
import websocket

MATCH_STR = "!test"
RESPONSE = "Hey there!"

TWITCH_USERNAME = "[REDACTED]"
TWITCH_PASSWORD = "[REDACTED]"
CHANNEL_NAME = "[REDACTED]"
GQL_API_URL = "https://gql.twitch.tv/gql"

def login_to_twitch(username, password):
    session = requests.Session()

    session.headers = {
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Accept-Language": "en-GB,en;q=0.9,en-US;q=0.8,lt;q=0.7",
    }

    resp1 = session.get("https://www.twitch.tv/directory")

    session.cookies.set(
        "api_token", "twilight.46cc59eee010864b5ddfa5bc17f457b8", domain="twitch.tv"
    )
    logging.debug(session.cookies)

    payload = {
        "username": username,
        "password": password,
        "client_id": "kimne78kx3ncx6brgo4mv6wki5h1ko",
        "undelete_user": False,
    }

    logging.debug(payload)
    resp2 = session.post("https://passport.twitch.tv/login", json=payload)
    logging.debug(resp2.text)

    json_dict = resp2.json()

    token = json_dict.get("access_token")

    if json_dict.get("error_code") == 3022:
        err_msg = json_dict.get("error")
        logging.error(err_msg)
        captcha_proof = json_dict.get("captcha_proof")
        code = input("Code from email ({}): ".format(json_dict.get("obscured_email")))
        code = code.strip()

        payload["captcha"] = {"proof": captcha_proof}
        payload["twitchguard_code"] = code

        logging.debug(payload)
        resp3 = session.post("https://passport.twitch.tv/login", json=payload)

        logging.debug(resp3.text)

        json_dict = resp3.json()

        token = json_dict.get("access_token")

    session.headers["Client-Id"] = "kimne78kx3ncx6brgo4mv6wki5h1ko"

    if token is not None:
        session.headers["Authorization"] = "OAuth {}".format(token)

    return session, token

def get_channel_id(session, channel):
    logging.info("Retrieving ID for channel {}".format(channel))

    payload = {
        "operationName": "PlaybackAccessToken",
        "variables": {
            "isLive": True,
            "login": channel.replace("#", ""),
            "isVod": False,
            "vodID": "",
            "playerType": "site",
        },
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "0828119ded1c13477966434e15800ff57ddacf13ba1911c129dc2200705b0712",
            }
        },
    }

    logging.debug(payload)
    resp = session.post(GQL_API_URL, json=payload)
    logging.debug(resp.text)

    json_dict = resp.json()

    value_str = json_dict.get("data", dict()).get("streamPlaybackAccessToken", dict()).get("value")
    if value_str is None:
        return
        
    value_dict = json.loads(value_str)

    channel_id = value_dict.get("channel_id")

    if channel_id is not None:
        logging.info(
            "Got channel ID for {} : {}".format(channel, channel_id)
        )

        return channel_id

    return None

def follow_channel(session, channel_id):
    payload = [
        {
            "operationName": "FollowButton_FollowUser",
            "variables": {
                "input": {
                    "disableNotifications": False,
                    "targetID": str(channel_id),
                }
            },
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "800e7346bdf7e5278a3c1d3f21b2b56e2639928f86815677a7126b093b2fdd08",
                }
            },
        }
    ]

    logging.debug(payload)
    resp = session.post(GQL_API_URL, json=payload)
    logging.debug(resp.text)

def connect_to_websocket(username, channel, token):
    ws = websocket.WebSocket()
    ws.connect(
        "wss://irc-ws.chat.twitch.tv/",
    )

    ws.send("CAP REQ :twitch.tv/tags twitch.tv/commands")
    ws.send("PASS oauth:{}".format(token))
    ws.send("NICK {}".format(username))
    ws.send("USER {} 8 * :{}".format(username, username))
    ws.send("JOIN {}".format(channel))

    return ws

def send_message(ws, channel, message):
    nonce = str(uuid.uuid4()).replace("-", "")

    ws.send("@client-nonce={} PRIVMSG {} :{}".format(nonce, channel, message))

def run_loop(ws, channel, match_str, response):
    while True:
        try:
            message = ws.recv()
        except Exception as e:
            logging.warning(e)
            break

        logging.debug(message)
        if message.startswith("PING"):
            ws.send("PONG")
        elif "PRIVMSG {} :".format(channel) in message:
            message = message.split("PRIVMSG {} :".format(channel))[-1]
            if match_str in message:
                send_message(ws, channel, response)

def main():
    logging.basicConfig(
        format="%(asctime)s [%(levelname)-5.5s]  %(message)s",
        level=logging.DEBUG,
    )

    websocket.enableTrace(True)

    session, token = login_to_twitch(TWITCH_USERNAME, TWITCH_PASSWORD)

    channel_id = get_channel_id(session, CHANNEL_NAME)
    
    follow_channel(session, channel_id)

    ws = connect_to_websocket(TWITCH_USERNAME, CHANNEL_NAME, token)
    
    run_loop(ws, CHANNEL_NAME, MATCH_STR, RESPONSE)

if __name__ == "__main__":
    main()
```

This is a proof of concept chatbot that replicates Discord self-botting concept on Twitch.
The following improvements could made for this code:

* Multithreading to support multiple channels and/or accounts - one thread for WS connection.
* Proxy support.
* Captcha solver integration for the cases when Twitch does ask for captcha.
* Email auto-verification.
* Randomization/spinning of response message so that Twitch does not discard it if multiple responses are sent in short timeframe.

