#!/bin/bash

payload=test_s3.json
content=${2:-application/json}

curl --data-binary @${payload} -H "Content-Type: ${content}" -v http://localhost:8080/invocations