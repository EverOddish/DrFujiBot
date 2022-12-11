#!/bin/bash

curl -H "Authorization: Bearer ${TWITCH_TOKEN}" -H "Client-Id: ${TWITCH_CLIENT_ID}" https://api.twitch.tv/helix/eventsub/subscriptions | python3 -m json.tool
