#!/bin/bash

# Get into the app directory
cd /dashdotdb || echo "can't find /dashdotdb. Was the image correctly build? Running dashdotdb should be expected to fail"
# it could be reasonable to exit 1 if we can't find the directory, but if we let
# the the application fail to start, it will be much more obvious in the
# container's logs what is happening. Hopefully the "echo-on-cd-failure" message
# will help diagnosing any potential problems.

FLASK_APP=dashdotdb flask db upgrade
# Run the app
gunicorn dashdotdb:app --workers 2 --threads 2 --bind 0.0.0.0:8080
