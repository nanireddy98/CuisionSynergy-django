from django.urls import path

from . import views
from accounts import views as AccountViews

urlpatterns = [
    path('', AccountViews.customer_dashboard,name='customer'),
    path('profile/', views.cprofile, name='cprofile'),
    path('my_orders/', views.my_orders, name='customer_my_orders'),
    path('order_detail/<int:order_number>/', views.order_detail, name='order_detail'),
]
