"""
Forms for JKH CRM application.
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Building, Request, RequestComment, UserProfile


class BuildingForm(forms.ModelForm):
    """Form for creating and editing buildings."""

    class Meta:
        model = Building
        fields = [
            'address', 'latitude', 'longitude', 'total_apartments',
            'total_area', 'year_built', 'description'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class RequestForm(forms.ModelForm):
    """Form for creating and editing requests."""

    class Meta:
        model = Request
        fields = [
            'title', 'type', 'description', 'priority', 'building',
            'apartment_number', 'floor', 'estimated_completion',
            'cost_estimate'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'estimated_completion': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}
            ),
        }


class RequestAssignForm(forms.ModelForm):
    """Form for assigning requests to workers."""

    class Meta:
        model = Request
        fields = ['assigned_to']
        widgets = {
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }


class RequestStatusForm(forms.ModelForm):
    """Form for updating request status."""

    class Meta:
        model = Request
        fields = ['status', 'actual_hours', 'final_cost']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class RequestCommentForm(forms.ModelForm):
    """Form for adding comments to requests."""

    class Meta:
        model = RequestComment
        fields = ['text', 'is_internal']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'is_internal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class UserRegistrationForm(UserCreationForm):
    """Extended registration form with profile information."""

    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        required=True,
        label='Роль'
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        label='Телефон'
    )
    address = forms.CharField(
        max_length=255,
        required=False,
        label='Адрес'
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password1', 'password2', 'role', 'phone', 'address'
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Create profile
            UserProfile.objects.create(
                user=user,
                role=self.cleaned_data['role'],
                phone=self.cleaned_data.get('phone'),
                address=self.cleaned_data.get('address')
            )
        return user


class UserEditForm(UserChangeForm):
    """Form for editing user information."""

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile."""

    class Meta:
        model = UserProfile
        fields = ['role', 'phone', 'address', 'is_active']