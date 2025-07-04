#!/bin/bash
set -e

echo "Waiting for database..."
while ! pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER"; do
    echo "Database not ready, waiting..."
    sleep 2
done
echo "Database is ready!"

echo "Applying database migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating API token..."
python manage.py create_api_token api_user --create-user || echo "API token already exists"

echo "Starting server..."
exec "$@" 