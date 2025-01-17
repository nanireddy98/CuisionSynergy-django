from django import forms

from .models import Vendor, OpeningHour
from accounts.validators import allow_only_images


class VendorForm(forms.ModelForm):
    """
    Form for creating and updating Vendor instances.
    Includes custom validation for the vendor_licence field.
    """
    vendor_licence = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}),
                                     validators=[allow_only_images])

    class Meta:
        model = Vendor
        fields = ['vendor_name', 'vendor_licence']


class OpeningHourForm(forms.ModelForm):
    """Form for creating and updating OpeningHour instances."""
    class Meta:
        model = OpeningHour
        fields = ['day', 'from_hour', 'to_hour', 'is_closed']
