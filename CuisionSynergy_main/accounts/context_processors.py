from django.conf import settings

from accounts.models import UserProfile
from vendor.models import Vendor


def get_vendor(request):
    """
   Retrieve the Vendor instance associated with the logged-in user.
   Returns a dictionary containing the vendor or None if not found.
    """
    try:
        vendor = Vendor.objects.get(user=request.user)
    except:
        vendor = None
    return dict(vendor=vendor)


def get_user_profile(request):
    """
    Retrieve the UserProfile instance associated with the logged-in user.
    Returns a dictionary containing the user profile or None if not found.
    """
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except:
        user_profile = None
    return dict(user_profile=user_profile)


def get_google_api_key(request):
    """
    Retrieve the Google API key from settings.
    Returns a dictionary containing the API key.
    """
    return {'GOOGLE_API_KEY': settings.GOOGLE_API_KEY}


def get_paypal_client_id(request):
    """
    Retrieve the PayPal Client ID from settings.
    Returns a dictionary containing the API key.
    """
    return {'PAYPAL_CLIENT_ID': settings.PAYPAL_CLIENT_ID}
