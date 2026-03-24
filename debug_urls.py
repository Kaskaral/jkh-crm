import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PythonProject6.settings')

# Добавляем папку проекта в путь
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Добавляем папку apps
apps_dir = os.path.join(project_dir, 'apps')
if apps_dir not in sys.path:
    sys.path.insert(0, apps_dir)

django.setup()

print("=== Django Settings Check ===")
print(f"BASE_DIR: {django.conf.settings.BASE_DIR}")
print(f"INSTALLED_APPS: {django.conf.settings.INSTALLED_APPS}")
print(f"sys.path: {sys.path}")

print("\n=== URL Configuration ===")
from django.urls import get_resolver
resolver = get_resolver()

print("URL patterns:")
for pattern in resolver.url_patterns:
    print(f"  - {pattern.pattern}")
    if hasattr(pattern, 'url_patterns'):
        for sub in pattern.url_patterns:
            print(f"    * {sub.pattern}")

print("\n=== Apps Check ===")
from django.apps import apps
print("Loaded apps:")
for app in apps.get_app_configs():
    print(f"  - {app.label}: {app.name}")