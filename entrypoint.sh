#!/bin/bash

FLASK_APP=dashdotdb flask db upgrade
# Run the app
gunicorn dashdotdb:app --workers 2 --threads 2 --bind 0.0.0.0:8080
