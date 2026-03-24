import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jkh_crm.settings')
django.setup()

from django.contrib.auth.models import User
from apps.core.models import UserProfile, Building, Request

# Создаем пользователей
admin_user = User.objects.create_superuser('admin', 'admin@jkh.local', 'admin123')
admin_user.first_name = 'Админ'
admin_user.last_name = 'Системы'
admin_user.save()

UserProfile.objects.create(user=admin_user, role='admin')

worker_user = User.objects.create_user('worker1', 'worker@jkh.local', 'worker123')
worker_user.first_name = 'Иван'
worker_user.last_name = 'Иванов'
worker_user.save()

UserProfile.objects.create(user=worker_user, role='worker', phone='+7 (999) 123-45-67')

# Создаем дома
building1 = Building.objects.create(
    address='ул. Ленина, д. 1',
    latitude=55.7558,
    longitude=37.6173,
    total_apartments=50,
    total_area=3500,
    year_built=1985,
    description='Пятиэтажный дом'
)

building2 = Building.objects.create(
    address='пр. Победы, д. 10',
    latitude=55.7512,
    longitude=37.6184,
    total_apartments=100,
    total_area=7000,
    year_built=2000,
    description='Девятиэтажный дом'
)

# Создаем заявки
Request.objects.create(
    title='Течет крыша',
    type='repair',
    description='В подъезде №2 на 5 этаже течет крыша после дождя',
    priority='high',
    status='new',
    building=building1,
    apartment_number='45',
    floor=5,
    created_by=admin_user
)

Request.objects.create(
    title='Не работает лифт',
    type='emergency',
    description='Лифт в подъезде №1 не работает уже 2 дня',
    priority='urgent',
    status='new',
    building=building2,
    created_by=admin_user
)

print("Тестовые данные созданы успешно!")
print("Логин админа: admin / admin123")
print("Логин рабочего: worker1 / worker123")