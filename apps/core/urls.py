"""
URL configuration for core app.
"""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('', views.dashboard_view, name='home'),

    # Buildings
    path('buildings/', views.building_list_view, name='building_list'),
    path('buildings/create/', views.building_create_view, name='building_create'),
    path('buildings/<int:pk>/edit/', views.building_edit_view, name='building_edit'),
    path('buildings/<int:pk>/delete/', views.building_delete_view, name='building_delete'),
    path('buildings/map/', views.building_map_view, name='building_map'),

    # Requests
    path('requests/', views.request_list_view, name='request_list'),
    path('requests/create/', views.request_create_view, name='request_create'),
    path('requests/<int:pk>/', views.request_detail_view, name='request_detail'),
    path('requests/<int:pk>/edit/', views.request_edit_view, name='request_edit'),
    path('requests/<int:pk>/assign/', views.request_assign_view, name='request_assign'),
    path('requests/<int:pk>/accept/', views.request_accept_view, name='request_accept'),
    path('requests/<int:pk>/update-status/', views.request_update_status_view, name='request_update_status'),

    # Users
    path('users/', views.user_list_view, name='user_list'),
    path('users/create/', views.user_create_view, name='user_create'),
    path('users/<int:pk>/edit/', views.user_edit_view, name='user_edit'),
    path('users/<int:pk>/delete/', views.user_delete_view, name='user_delete'),

    # Notifications
    path('notifications/', views.notification_list_view, name='notification_list'),
    path('notifications/<int:pk>/read/', views.notification_mark_read_view, name='notification_mark_read'),
    path('notifications/mark-all-read/', views.notification_mark_all_read_view, name='notification_mark_all_read'),

    # API endpoints
    path('api/buildings/', views.api_buildings_json, name='api_buildings'),
    path('api/buildings/<int:building_id>/requests/', views.api_requests_by_building, name='api_requests_by_building'),
]