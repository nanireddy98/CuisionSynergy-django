from django.contrib import admin
from .models import Category, FoodItem


class CategoryAdmin(admin.ModelAdmin):
    """Define an admin class for the Category model"""
    prepopulated_fields = {'slug': ('category_name',)}  # Automatically populate the 'slug' field based on the 'category_name' field
    list_display = ('category_name', 'vendor', 'updated_at')  # Display fields in the admin list view for Category
    search_fields = ('category_name', 'vendor__vendor_name')  # Enable search functionality for these fields in the admin interface


class FoodItemAdmin(admin.ModelAdmin):
    """Define an admin class for the FoodItem model"""
    prepopulated_fields = {'slug': ('food_title',)}  # Automatically populate the 'slug' field based on the 'food_title' field
    list_display = ('food_title', 'category', 'vendor', 'price', 'is_available', 'updated_at')  # Display fields in the admin list view for FoodItem
    search_fields = ('food_title', 'category__category_name', 'vendor__vendor_name','price')  # Enable search functionality for these fields in the admin interface
    list_filter = ('is_available',)  # Add a filter for the 'is_available' field in the admin list view


admin.site.register(Category, CategoryAdmin)  # Register the Category model with the CategoryAdmin class
admin.site.register(FoodItem, FoodItemAdmin)  # Register the FoodItem model with the FoodItemAdmin class
