#!/bin/bash
source venv/bin/activate
nohup python app.py > flask.log 2>&1 &
echo "Flask app started in background. Logs: flask.log"
