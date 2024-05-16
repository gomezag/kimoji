#!/bin/bash

cd /code
set -m

fastapi run kimoji/app.py --port 8000 & 1>/dev/null 2>/dev/null

# Maximum number of seconds to wait for the endpoint to respond
timeout=60 # 1 minutes
start_time=$(date +%s)
url="http://localhost:8000"
# Wait until the endpoint responds or timeout is reached
while ! curl --max-time 2 "$url" ; do
    echo "Waiting for $url to respond... Current status: $response"
    sleep 2 # wait for 5 seconds before check again

    # Check if the timeout has been reached
    current_time=$(date +%s)
    if (( current_time - start_time > timeout )); then
        echo "Timeout reached. $url did not respond in $timeout seconds."
        exit 1
    fi
done

if [ $1 ]; then
  pytest tests --junitxml=junit/test-results.xml
fi
python start_db.py

if ! [ $1 ]; then
  fg %1
fi
