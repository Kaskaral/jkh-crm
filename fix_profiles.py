import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PythonProject6.settings')
django.setup()

from django.contrib.auth.models import User
from apps.core.models import UserProfile

# Создаем профили для всех пользователей, у которых их нет
for user in User.objects.all():
    if not hasattr(user, 'profile'):
        role = 'admin' if user.is_superuser else 'worker'
        UserProfile.objects.create(user=user, role=role)
        print(f"Создан профиль для пользователя: {user.username} (роль: {role})")

print("Все профили созданы успешно!")