from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, UserProfile


class CustomUserAdmin(UserAdmin):
    """
    Custom admin panel configuration for the User model.
    Extends the default UserAdmin to include custom fields and settings.
    """
    list_display = ('email', 'first_name', 'last_name', 'username', 'role', 'is_active')  # Fields displayed in the admin list view
    ordering = ('-date_joined',)  # Order users by date joined, descending
    filter_horizontal = ()  # No horizontal filters
    list_filter = ()  # No filters applied to the list view
    fieldsets = ()  # Default fieldsets from UserAdmin are used


# Register the User model with the customized admin interface
admin.site.register(User, CustomUserAdmin)

# Register the UserProfile model with the default admin interface
admin.site.register(UserProfile)
