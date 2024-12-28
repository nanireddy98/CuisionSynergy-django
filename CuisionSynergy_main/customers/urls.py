from django.urls import path

from . import views
from accounts import views as AccountViews

urlpatterns = [
    path('', AccountViews.customer_dashboard,name='customer'),
    path('profile/', views.cprofile, name='cprofile'),
]
