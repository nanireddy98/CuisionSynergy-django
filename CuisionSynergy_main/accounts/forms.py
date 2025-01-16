from django import forms

from .models import User, UserProfile
from .validators import allow_only_images


class UserForm(forms.ModelForm):
    """
    Form for creating and updating User instances.
    Includes password and confirm_password fields with validation.
    """
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password']

    def clean(self):
        """
        Validates that the password and confirm_password fields match.
        """
        cleaned_data = super(UserForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")


class UserProfileForm(forms.ModelForm):
    """
    Form for creating and updating UserProfile instances.
    Includes profile and cover photos with image validation.
    """
    profile_photo = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}),
                                    validators=[allow_only_images])
    cover_photo = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}),
                                  validators=[allow_only_images])

    # latitude = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    # longitude = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = UserProfile
        fields = ['profile_photo', 'cover_photo', 'address', 'country', 'state', 'city', 'pincode',
                  'latitude', 'longitude']

    def __init__(self, *args, **kwargs):
        """
        Initializes the form and sets latitude and longitude fields as read-only.
        """
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if field == 'latitude' or field == 'longitude':
                self.fields[field].widget.attrs['readonly'] = 'readonly'


class UserInfoForm(forms.ModelForm):
    """
    Form for updating basic User information.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number']
