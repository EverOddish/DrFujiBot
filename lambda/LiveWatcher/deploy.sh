#!/bin/bash
zip -r LiveWatcher.zip .

aws lambda update-function-code --function-name LiveWatcher --zip-file fileb://LiveWatcher.zip --profile pchal
