#!/bin/sh

# Wait for PostgreSQL to be ready
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done

# Apply database migrations
python manage.py migrate

# Start the Django server
exec "$@"