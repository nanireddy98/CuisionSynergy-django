from django.contrib import admin
from .models import Vendor, OpeningHour


class VendorAdmin(admin.ModelAdmin):
    """Customizes the admin interface for the Vendor model."""
    list_display = ('user', 'vendor_name', 'is_approved', 'created_at')  # Fields to display in the admin list view
    list_display_links = ('user', 'vendor_name')  # Fields that link to the edit page
    list_editable = ('is_approved',)  # Fields that can be edited directly in the list view


class OpeningHourAdmin(admin.ModelAdmin):
    """Customizes the admin interface for the OpeningHour model."""
    list_display = ('vendor', 'day', 'from_hour', 'to_hour')  # Fields to display in the admin list view


# Register the models with their respective admin configurations
admin.site.register(Vendor, VendorAdmin)
admin.site.register(OpeningHour, OpeningHourAdmin)
