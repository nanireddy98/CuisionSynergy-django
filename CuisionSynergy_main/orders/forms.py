from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    """Form class to handle the Order model's data entry and validation"""
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone', 'email', 'address', 'country', 'state', 'city', 'pin_code']
