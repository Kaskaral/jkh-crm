#!/bin/bash
python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn PythonProject6.wsgi:application