#!/bin/bash

# Init the database
FLASK_APP=dashdotdb uv run --no-group dev flask db upgrade
# Run the app
uv run --no-group dev gunicorn dashdotdb:app --workers 2 --threads 2 --bind 0.0.0.0:8080
