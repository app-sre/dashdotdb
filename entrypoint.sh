#!/bin/bash

FLASK_APP=dashdotdb flask db upgrade

gunicorn dashdotdb:app --workers 1 --threads 8 --bind 0.0.0.0:8080
