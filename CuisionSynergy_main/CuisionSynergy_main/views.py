from django.shortcuts import render, redirect
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django.contrib import messages

from vendor.models import Vendor
from .utils import get_or_set_current_location


def home(request):
    """
    Renders the home page with a list of vendors within a specified distance based on the user's location.

    - If a valid location is found, vendors within 2000 km of the user's location are filtered and ordered by proximity.
    - If no location is found, only approved and active vendors are displayed (limited to 8 vendors).
    """
    location = get_or_set_current_location(request)
    if location is not None:
        # Unpack latitude and longitude from the user's location
        lng, lat = location
        pnt = GEOSGeometry(f'POINT({lng} {lat})')  # Create a Point object with the user's location

        # Find vendors within 2000 km from the user's location
        vendors = Vendor.objects.filter(user_profile__location__distance_lte=(pnt, D(km=2000))).annotate(
            distance=Distance("user_profile__location", pnt)).order_by("distance")

        # Annotate each vendor with the distance to the user, rounded to 1 decimal place
        for v in vendors:
            v.kms = round(v.distance.km, 1)
    else:
        vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]
    context = {
        'vendors': vendors
    }
    return render(request, "home.html", context)


def about_us(request):
    return render(request, "about-us.html")


def career(request):
    return render(request, "career.html")


def press(request):
    return render(request, "press.html")


def blogs(request):
    return render(request, "blogs.html")


def terms_conditions(request):
    return render(request, "terms_conditions.html")


def privacy_policy(request):
    return render(request, "privacy_policy.html")


def cookie_policy(request):
    return render(request, "cookie_policy.html")
