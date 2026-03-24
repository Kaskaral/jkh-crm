"""
Models for JKH CRM application.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.apps import apps

class UserProfile(models.Model):
    """Extended user profile with role information."""

    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('worker', 'Рабочий'),
        ('manager', 'Менеджер'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='worker')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'


class Building(models.Model):
    """Building information for JKH management."""

    address = models.CharField(max_length=255, unique=True)
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
    total_apartments = models.IntegerField(default=0)
    total_area = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    year_built = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = 'Дом'
        verbose_name_plural = 'Дома'
        ordering = ['address']


class Request(models.Model):
    """Main request/ticket model for JKH issues."""

    TYPE_CHOICES = [
        ('repair', 'Ремонт'),
        ('maintenance', 'Обслуживание'),
        ('complaint', 'Жалоба'),
        ('inquiry', 'Запрос информации'),
        ('emergency', 'Аварийная ситуация'),
    ]

    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('assigned', 'Назначена'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершена'),
        ('cancelled', 'Отменена'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
        ('urgent', 'Срочный'),
    ]

    # Basic information
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')

    # Location information
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='requests')
    apartment_number = models.CharField(max_length=10, blank=True, null=True)
    floor = models.IntegerField(null=True, blank=True)

    # Assignment
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_requests'
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_requests'
    )

    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Additional info
    estimated_completion = models.DateTimeField(null=True, blank=True)
    actual_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    cost_estimate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Images (optional)
    image1 = models.ImageField(upload_to='requests/%Y/%m/%d/', blank=True, null=True)
    image2 = models.ImageField(upload_to='requests/%Y/%m/%d/', blank=True, null=True)
    image3 = models.ImageField(upload_to='requests/%Y/%m/%d/', blank=True, null=True)

    def __str__(self):
        return f"{self.get_type_display()} - {self.title}"

    def save(self, *args, **kwargs):
        # Update assigned_at when request is assigned
        if self.assigned_to and not self.assigned_at:
            self.assigned_at = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']


class RequestComment(models.Model):
    """Comments on requests for communication."""

    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_internal = models.BooleanField(default=False)  # Internal vs customer visible

    def __str__(self):
        return f"Comment by {self.author.username} on {self.request.title}"

    class Meta:
        verbose_name = 'Комментарий к заявке'
        verbose_name_plural = 'Комментарии к заявкам'
        ordering = ['created_at']


class RequestHistory(models.Model):
    """Track changes to requests for audit trail."""

    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    field_changed = models.CharField(max_length=50)
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.request.title} - {self.field_changed}"

    class Meta:
        verbose_name = 'История изменений'
        verbose_name_plural = 'Истории изменений'
        ordering = ['-changed_at']


class BuildingImage(models.Model):
    """Images of buildings for documentation."""

    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='buildings/%Y/%m/%d/')
    description = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.building.address}"

    class Meta:
        verbose_name = 'Изображение дома'
        verbose_name_plural = 'Изображения домов'


class Notification(models.Model):
    """User notifications for important events."""

    TYPE_CHOICES = [
        ('request_assigned', 'Заявка назначена'),
        ('request_completed', 'Заявка завершена'),
        ('request_updated', 'Заявка обновлена'),
        ('new_request', 'Новая заявка'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    related_request = models.ForeignKey(
        Request,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )

    def __str__(self):
        return f"{self.get_type_display()} for {self.user.username}"

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-created_at']

default_app_config = 'apps.core.apps.CoreConfig'