#!/bin/bash

# Init the database
FLASK_APP=dashdotdb flask db upgrade
# Run the app
gunicorn dashdotdb:app --workers 1 --threads 8 --bind 0.0.0.0:8080
