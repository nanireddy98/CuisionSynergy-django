from django.urls import path

from .views import ContactView, ThankyouView

urlpatterns = [
    path('', ContactView.as_view(), name='contact_us'),
    path("thankyou/", ThankyouView.as_view(), name="thankyou"),
]
