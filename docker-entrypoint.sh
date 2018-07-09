#!/bin/bash

# Collect static files
echo "Collect static files"
python3 manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
python3 manage.py migrate

# set ownership
chown -R www-data:www-data /code

# Start server
echo "Starting server"
python3 manage.py runmodwsgi --user=www-data --group=www-data --port=80
