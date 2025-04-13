#!/bin/sh
set -e

echo "Running migrations..."
python manage.py migrate


echo "Starting Uvicorn server with Gunicorn and multiple workers..."
exec gunicorn spotifyCloneBackend.asgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --worker-class uvicorn.workers.UvicornWorker