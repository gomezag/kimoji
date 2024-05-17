#!/bin/bash

cd /code
set -m

fastapi run kimoji/app.py --port 8000 & 1>/dev/null 2>/dev/null
python start_db.py

if [ $1 ]; then
  pytest tests --junitxml=/results/test-results.xml
fi
if ! [ $1 ]; then
  fg %1
fi
