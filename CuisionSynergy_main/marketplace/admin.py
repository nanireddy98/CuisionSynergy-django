from django.contrib import admin

from .models import Cart, Tax


class CartAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Cart model.
    Displays user, food item, quantity, and last updated timestamp.
    """
    list_display = ('user', 'fooditem', 'quantity', 'updated_at')  # Fields to be displayed in the admin list view for Cart


class TaxAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Tax model.
    Displays tax type, percentage, and active status.
    """
    list_display = ('tax_type', 'tax_percentage', 'is_active')  # Fields to be displayed in the admin list view for Tax


# Register the Cart model with its admin configuration
admin.site.register(Cart, CartAdmin)
admin.site.register(Tax, TaxAdmin)
