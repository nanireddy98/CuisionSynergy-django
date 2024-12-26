from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance

from vendor.models import Vendor
from .utils import get_or_set_current_location

# def home(request):
#     return HttpResponse("<h1>Hello World<h1>")


def home(request):
    location = get_or_set_current_location(request)
    if location is not None:
        lng, lat = location
        pnt = GEOSGeometry(f'POINT({lng} {lat})')

        vendors = Vendor.objects.filter(user_profile__location__distance_lte=(pnt, D(km=2000))).annotate(
            distance=Distance("user_profile__location", pnt)).order_by("distance")

        for v in vendors:
            v.kms = round(v.distance.km, 1)
    else:
        vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]
    context = {
        'vendors': vendors
    }
    return render(request, "home.html", context)
