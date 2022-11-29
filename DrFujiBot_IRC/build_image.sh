#!/bin/sh
docker build -t drfujibot .
docker tag drfujibot:latest 256140028858.dkr.ecr.us-east-2.amazonaws.com/drfujibot:latest
docker push 256140028858.dkr.ecr.us-east-2.amazonaws.com/drfujibot:latest
