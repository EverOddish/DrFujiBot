#!/bin/bash

curl -X DELETE -H "Authorization: Bearer ${TWITCH_TOKEN}" -H "Client-Id: ${TWITCH_CLIENT_ID}" "https://api.twitch.tv/helix/eventsub/subscriptions?id=$1"
