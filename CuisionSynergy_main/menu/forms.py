from django import forms

from .models import Category, FoodItem
from accounts.validators import allow_only_images


class CategoryForm(forms.ModelForm):
    """Form for creating or updating Category objects"""
    class Meta:
        model = Category
        fields = ['category_name', 'description']


class FoodItemForm(forms.ModelForm):
    """Form for creating or updating FoodItem objects"""
    image = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info w-100'}), validators=[allow_only_images])

    class Meta:
        model = FoodItem
        fields = ['category', 'food_title', 'description', 'price', 'image', 'is_available']
