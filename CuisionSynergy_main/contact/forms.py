from django import forms


class ContactForm(forms.Form):
    """A form for users to submit contact messages."""
    email = forms.EmailField(widget=forms.TextInput(attrs={"placeholder": "Email address"}))
    subject = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Subject"}))
    message = forms.CharField(widget=forms.Textarea(attrs={"placeholder": "Type Text"}))
