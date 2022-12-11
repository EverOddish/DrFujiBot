#!/bin/bash
zip -r POSTHandler.zip .

aws lambda update-function-code --function-name POSTHandler --zip-file fileb://POSTHandler.zip --profile pchal
