#!/bin/bash
set -e

echo "🔧 Applying database migrations..."
python manage.py migrate --noinput

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

echo "Create SUPERSUS"
python manage.py create_superuser_if_not_exists

echo "✅ Starting Gunicorn..."
exec gunicorn PythonProject6.wsgi:application

