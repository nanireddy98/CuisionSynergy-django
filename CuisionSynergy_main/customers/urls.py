from django.urls import path

from . import views
from accounts import views as AccountViews

urlpatterns = [
    # Customer dashboard view
    path('', AccountViews.customer_dashboard,name='customer'),

    # Customer profile view
    path('profile/', views.cprofile, name='cprofile'),

    # View for listing customer's orders
    path('my_orders/', views.my_orders, name='customer_my_orders'),

    # Detailed view for a specific order, identified by order_number
    path('order_detail/<int:order_number>/', views.order_detail, name='order_detail'),
]
