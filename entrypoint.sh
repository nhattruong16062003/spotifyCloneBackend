#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate

echo "Starting Gunicorn server..."
exec gunicorn spotifyCloneBackend.wsgi:application --bind 0.0.0.0:8000 --workers=1
