"""
Views for JKH CRM application.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from .models import (
    Building, Request, RequestComment, RequestHistory,
    UserProfile, Notification
)
from .forms import (
    BuildingForm, RequestForm, RequestAssignForm,
    RequestStatusForm, RequestCommentForm,
    UserRegistrationForm, UserEditForm, UserProfileForm
)
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.models import User

def is_admin(user):
    """Check if user is admin."""
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.role == 'admin'


def is_worker(user):
    """Check if user is worker."""
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.role == 'worker'


def is_manager(user):
    """Check if user is manager."""
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.role == 'manager'


def login_view(request):
    """Login view."""
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('core:dashboard')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')

    return render(request, 'core/login.html')


@login_required
def logout_view(request):
    """Logout view."""
    logout(request)
    messages.info(request, 'Вы успешно вышли из системы.')
    return redirect('core:login')


@login_required
def dashboard_view(request):
    """Main dashboard view."""
    user = request.user

    # Проверяем, есть ли у пользователя профиль, если нет - создаем
    if not hasattr(user, 'profile'):
        from .models import UserProfile
        UserProfile.objects.create(user=user, role='admin')

    # Common statistics
    total_requests = Request.objects.count()
    pending_requests = Request.objects.filter(status='new').count()
    in_progress_requests = Request.objects.filter(status='in_progress').count()
    completed_requests = Request.objects.filter(status='completed').count()

    # Get recent requests
    recent_requests = Request.objects.all().order_by('-created_at')[:10]
    buildings = Building.objects.all()

    context = {
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'in_progress_requests': in_progress_requests,
        'completed_requests': completed_requests,
        'recent_requests': recent_requests,
        'buildings': buildings,
        'user': user,
    }

    return render(request, 'core/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def building_list_view(request):
    """List all buildings."""
    buildings = Building.objects.all().order_by('address')
    return render(request, 'core/building_list.html', {'buildings': buildings})


@login_required
@user_passes_test(is_admin)
def building_create_view(request):
    """Create new building."""
    if request.method == 'POST':
        form = BuildingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Дом успешно создан.')
            return redirect('core:building_list')  # ← Исправлено здесь!
    else:
        form = BuildingForm()

    return render(request, 'core/building_form.html', {'form': form, 'action': 'create'})
@login_required
@user_passes_test(is_admin)
def building_edit_view(request, pk):
    """Edit existing building."""
    building = get_object_or_404(Building, pk=pk)

    if request.method == 'POST':
        form = BuildingForm(request.POST, instance=building)
        if form.is_valid():
            form.save()
            messages.success(request, 'Дом успешно обновлен.')
            return redirect('core:building_list')
    else:
        form = BuildingForm(instance=building)

    return render(request, 'core/building_form.html', {'form': form, 'action': 'edit', 'building': building})


@login_required
@user_passes_test(is_admin)
def building_delete_view(request, pk):
    """Delete building."""
    building = get_object_or_404(Building, pk=pk)

    if request.method == 'POST':
        building.delete()
        messages.success(request, 'Дом успешно удален.')
        return redirect('core:building_list')

    return render(request, 'core/building_confirm_delete.html', {'building': building})


@login_required
def request_list_view(request):
    """List all requests with filtering."""
    user = request.user
    queryset = Request.objects.all()

    # Filter by user role
    if user.profile.role == 'worker':
        queryset = queryset.filter(
            Q(assigned_to=user) | Q(status='new')
        )

    # Apply filters from GET parameters
    status = request.GET.get('status')
    type_filter = request.GET.get('type')
    priority = request.GET.get('priority')
    building_id = request.GET.get('building')

    if status:
        queryset = queryset.filter(status=status)
    if type_filter:
        queryset = queryset.filter(type=type_filter)
    if priority:
        queryset = queryset.filter(priority=priority)
    if building_id:
        queryset = queryset.filter(building_id=building_id)

    # Order by creation date
    requests = queryset.order_by('-created_at')

    # Get filter options
    buildings = Building.objects.all()

    context = {
        'requests': requests,
        'buildings': buildings,
        'selected_status': status,
        'selected_type': type_filter,
        'selected_priority': priority,
        'selected_building': building_id,
        'user_role': user.profile.role,
    }

    return render(request, 'core/request_list.html', context)


@login_required
def request_detail_view(request, pk):
    """View request details."""
    req = get_object_or_404(Request, pk=pk)
    user = request.user

    # Check permissions
    if user.profile.role == 'worker' and req.assigned_to != user and req.status != 'new':
        messages.error(request, 'У вас нет доступа к этой заявке.')
        return redirect('core:request_list')

    # Get comments
    comments = req.comments.all().order_by('created_at')

    # Handle comment form
    if request.method == 'POST' and 'add_comment' in request.POST:
        comment_form = RequestCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.request = req
            comment.author = user
            comment.save()

            # Create notification for assigned worker
            if req.assigned_to and req.assigned_to != user:
                Notification.objects.create(
                    user=req.assigned_to,
                    type='request_updated',
                    message=f'Новый комментарий к заявке: {req.title}',
                    related_request=req
                )

            messages.success(request, 'Комментарий добавлен.')
            return redirect('core:request_detail', pk=pk)
    else:
        comment_form = RequestCommentForm()

    context = {
        'request': req,
        'comments': comments,
        'comment_form': comment_form,
        'user_role': user.profile.role,
        'can_assign': user.profile.role in ['admin', 'manager'] and not req.assigned_to,
        'can_update_status': user.profile.role in ['admin', 'manager'] or (
                    user.profile.role == 'worker' and req.assigned_to == user),
    }

    return render(request, 'core/request_detail.html', context)


@login_required
@user_passes_test(lambda u: u.profile.role in ['admin', 'manager'])
def request_create_view(request):
    """Create new request."""
    if request.method == 'POST':
        form = RequestForm(request.POST, request.FILES)
        if form.is_valid():
            req = form.save(commit=False)
            req.created_by = request.user
            req.save()

            # Create notification for all workers
            workers = User.objects.filter(profile__role='worker', profile__is_active=True)
            for worker in workers:
                Notification.objects.create(
                    user=worker,
                    type='new_request',
                    message=f'Новая заявка: {req.title}',
                    related_request=req
                )

            messages.success(request, 'Заявка успешно создана.')
            return redirect('core:request_detail', pk=req.pk)
    else:
        form = RequestForm()

    return render(request, 'core/request_form.html', {'form': form, 'action': 'create'})


@login_required
@user_passes_test(lambda u: u.profile.role in ['admin', 'manager'])
def request_edit_view(request, pk):
    """Edit existing request."""
    req = get_object_or_404(Request, pk=pk)

    if request.method == 'POST':
        form = RequestForm(request.POST, request.FILES, instance=req)
        if form.is_valid():
            form.save()
            messages.success(request, 'Заявка успешно обновлена.')
            return redirect('core:request_detail', pk=pk)
    else:
        form = RequestForm(instance=req)

    return render(request, 'core/request_form.html', {'form': form, 'action': 'edit', 'request': req})


@login_required
@user_passes_test(lambda u: u.profile.role in ['admin', 'manager'])
def request_assign_view(request, pk):
    """Assign request to worker."""
    req = get_object_or_404(Request, pk=pk)

    if req.assigned_to:
        messages.error(request, 'Заявка уже назначена.')
        return redirect('core:request_detail', pk=pk)

    if request.method == 'POST':
        form = RequestAssignForm(request.POST, instance=req)
        if form.is_valid():
            req = form.save(commit=False)
            req.status = 'assigned'
            req.save()

            # Create notification for worker
            if req.assigned_to:
                Notification.objects.create(
                    user=req.assigned_to,
                    type='request_assigned',
                    message=f'Вам назначена заявка: {req.title}',
                    related_request=req
                )

            messages.success(request, f'Заявка назначена {req.assigned_to.username}.')
            return redirect('core:request_detail', pk=pk)
    else:
        form = RequestAssignForm(instance=req)

    # Get available workers
    workers = User.objects.filter(profile__role='worker', profile__is_active=True)

    return render(request, 'core/request_assign.html', {'form': form, 'request': req, 'workers': workers})


@login_required
def request_accept_view(request, pk):
    """Worker accepts request."""
    req = get_object_or_404(Request, pk=pk)
    user = request.user

    # Only workers can accept, and only if not assigned yet
    if user.profile.role != 'worker':
        messages.error(request, 'Только рабочие могут принимать заявки.')
        return redirect('core:request_detail', pk=pk)

    if req.assigned_to:
        messages.error(request, 'Заявка уже назначена.')
        return redirect('core:request_detail', pk=pk)

    # Assign to current user
    req.assigned_to = user
    req.status = 'assigned'
    req.save()

    # Create notification for admin/manager
    admins = User.objects.filter(profile__role__in=['admin', 'manager'])
    for admin in admins:
        Notification.objects.create(
            user=admin,
            type='request_assigned',
            message=f'Заявка "{req.title}" принята {user.username}',
            related_request=req
        )

    messages.success(request, 'Вы приняли заявку.')
    return redirect('core:request_detail', pk=pk)


@login_required
def request_update_status_view(request, pk):
    """Update request status."""
    req = get_object_or_404(Request, pk=pk)
    user = request.user

    # Check permissions
    if user.profile.role not in ['admin', 'manager'] and (user.profile.role != 'worker' or req.assigned_to != user):
        messages.error(request, 'У вас нет прав для изменения статуса.')
        return redirect('core:request_detail', pk=pk)

    if request.method == 'POST':
        status = request.POST.get('status')
        actual_hours = request.POST.get('actual_hours', '0')
        final_cost = request.POST.get('final_cost', '0')

        if status:
            req.status = status

            if status == 'completed':
                from django.utils import timezone
                req.completed_at = timezone.now()
                try:
                    req.actual_hours = float(actual_hours) if actual_hours else 0
                    req.final_cost = float(final_cost) if final_cost else 0
                except (ValueError, TypeError):
                    req.actual_hours = 0
                    req.final_cost = 0

            req.save()

            # Create notification
            if req.created_by:
                Notification.objects.create(
                    user=req.created_by,
                    type='request_completed' if status == 'completed' else 'request_updated',
                    message=f'Статус заявки "{req.title}" изменен на {req.get_status_display()}',
                    related_request=req
                )

            messages.success(request, 'Статус заявки обновлен.')
            return redirect('core:request_detail', pk=pk)

    # For GET requests, create a form with current status
    from .forms import RequestStatusForm
    form = RequestStatusForm(instance=req)

    return render(request, 'core/request_update_status.html', {'form': form, 'request': req})

@login_required
@user_passes_test(is_admin)
def user_list_view(request):
    """List all users."""
    from django.contrib.auth.models import User
    users = User.objects.select_related('profile').all().order_by('username')
    return render(request, 'core/user_list.html', {'users': users})

@login_required
@user_passes_test(is_admin)
# apps/core/views.py
def user_create_view(request):
    if request.user.profile.role not in ['admin', 'manager']:
        messages.error(request, 'Недостаточно прав для создания пользователя.')
        return redirect('core:request_list')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Пользователь успешно создан.')
            return redirect('core:user_list')
    else:
        form = UserRegistrationForm()

    return render(request, 'core/user_form.html', {'form': form, 'action': 'create'})
@login_required
@user_passes_test(is_admin)
def user_edit_view(request, pk):
    """Edit existing user."""
    user = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, instance=user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, f'Пользователь {user.username} успешно обновлен.')
            return redirect('core:user_list')
    else:
        user_form = UserEditForm(instance=user)
        profile_form = UserProfileForm(instance=user.profile)

    return render(request, 'core/user_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_obj': user
    })


@login_required
@user_passes_test(is_admin)
def user_delete_view(request, pk):
    """Delete user."""
    user = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'Пользователь {username} успешно удален.')
        return redirect('core:user_list')

    return render(request, 'core/user_confirm_delete.html', {'user': user})


@login_required
def notification_list_view(request):
    """List user notifications."""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/notification_list.html', {'notifications': notifications})


@login_required
def notification_mark_read_view(request, pk):
    """Mark notification as read."""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('core:notification_list')


@login_required
def notification_mark_all_read_view(request):
    """Mark all notifications as read."""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, 'Все уведомления отмечены как прочитанные.')
    return redirect('core:notification_list')


@login_required
def building_map_view(request):
    """Map view of buildings with requests."""
    buildings = Building.objects.all()

    # Фильтруем дома с координатами для отдельного списка
    buildings_with_coordinates = []
    for building in buildings:
        if building.latitude and building.longitude:
            buildings_with_coordinates.append(building)

    context = {
        'buildings': buildings,
        'buildings_with_coordinates': buildings_with_coordinates,
    }

    return render(request, 'core/building_map.html', context)

@login_required
def api_buildings_json(request):
    """API endpoint for buildings data."""
    buildings = Building.objects.all()
    data = []

    for building in buildings:
        requests = building.requests.all()
        data.append({
            'id': building.id,
            'address': building.address,
            'latitude': float(building.latitude) if building.latitude else None,
            'longitude': float(building.longitude) if building.longitude else None,
            'requests_count': requests.count(),
            'pending_requests': requests.filter(status='new').count(),
            'requests': [
                {
                    'id': req.id,
                    'title': req.title,
                    'type': req.get_type_display(),
                    'status': req.get_status_display(),
                    'priority': req.get_priority_display(),
                    'created_at': req.created_at.isoformat(),
                }
                for req in requests[:5]  # Limit to 5 recent requests
            ]
        })

    return JsonResponse(data, safe=False)


@login_required
def api_requests_by_building(request, building_id):
    """API endpoint for requests by building."""
    building = get_object_or_404(Building, pk=building_id)
    requests = building.requests.all().order_by('-created_at')

    data = [
        {
            'id': req.id,
            'title': req.title,
            'type': req.get_type_display(),
            'status': req.get_status_display(),
            'priority': req.get_priority_display(),
            'created_at': req.created_at.isoformat(),
            'assigned_to': req.assigned_to.username if req.assigned_to else None,
        }
        for req in requests
    ]

    return JsonResponse(data, safe=False)