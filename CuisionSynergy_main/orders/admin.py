from django.contrib import admin

from .models import Payment, Order, OrderedFood


class OrderedFoodInline(admin.TabularInline):
    """Inline class to display the OrderedFood related data within the Order model in the admin interface"""
    model = OrderedFood
    readonly_fields = ['order', 'payment', 'user', 'fooditem', 'quantity', 'price', 'amount']
    extra = 0  # No extra empty forms will be shown by default


class OrderAdmin(admin.ModelAdmin):
    """Admin configuration for the Order model"""
    list_display = ['order_number', 'name', 'phone', 'email', 'payment_method', 'status', 'order_placed_to', 'is_ordered']
    inlines = [OrderedFoodInline]  # Including the OrderedFoodInline to show related OrderedFood data inline in the Order form


# Register the Payment, Order, and OrderedFood models to make them available in the Django admin interface
admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderedFood)
