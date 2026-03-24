"""
Admin configuration for core app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    UserProfile, Building, Request, RequestComment,
    RequestHistory, Notification
)


class UserProfileInline(admin.StackedInline):
    """Inline admin for user profile."""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профили'


class UserAdmin(BaseUserAdmin):
    """Extended user admin with profile."""
    inlines = [UserProfileInline]


class BuildingAdmin(admin.ModelAdmin):
    """Admin for buildings."""
    list_display = ['address', 'total_apartments', 'year_built', 'created_at']
    search_fields = ['address']
    list_filter = ['year_built']
    ordering = ['address']


class RequestAdmin(admin.ModelAdmin):
    """Admin for requests."""
    list_display = [
        'title', 'type', 'status', 'priority', 'building',
        'assigned_to', 'created_by', 'created_at'
    ]
    list_filter = ['status', 'type', 'priority', 'building']
    search_fields = ['title', 'description']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


class RequestCommentAdmin(admin.ModelAdmin):
    """Admin for request comments."""
    list_display = ['request', 'author', 'created_at', 'is_internal']
    list_filter = ['is_internal', 'created_at']
    search_fields = ['text']


class RequestHistoryAdmin(admin.ModelAdmin):
    """Admin for request history."""
    list_display = ['request', 'changed_by', 'field_changed', 'changed_at']
    list_filter = ['field_changed', 'changed_at']
    search_fields = ['old_value', 'new_value']
    date_hierarchy = 'changed_at'


#class BuildingImageAdmin(admin.ModelAdmin):
 #   """Admin for building images."""
   # list_display = ['building', 'description', 'uploaded_at']
   # list_filter = ['uploaded_at']


class NotificationAdmin(admin.ModelAdmin):
    """Admin for notifications."""
    list_display = ['user', 'type', 'is_read', 'created_at', 'related_request']
    list_filter = ['type', 'is_read', 'created_at']
    search_fields = ['message']


# Unregister and register with custom admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register other models
admin.site.register(Building, BuildingAdmin)
admin.site.register(Request, RequestAdmin)
admin.site.register(RequestComment, RequestCommentAdmin)
admin.site.register(RequestHistory, RequestHistoryAdmin)
#admin.site.register(BuildingImage, BuildingImageAdmin)
admin.site.register(Notification, NotificationAdmin)