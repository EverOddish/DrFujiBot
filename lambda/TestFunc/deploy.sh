#!/bin/bash
zip -r TestFunc.zip .

aws lambda update-function-code --function-name TestFunc --zip-file fileb://TestFunc.zip --profile pchal
