#!/bin/bash
twitch event trigger subscribe -F ${API_GATEWAY_URL} -s ${TWITCH_WEBHOOK_SECRET}
