from django.urls import path
from . import views

urlpatterns = [
    # placing an order
    path('place_order/', views.place_order, name='place_order'),

    # processing payments
    path('payment/', views.payments, name='payments'),

    # completing the order
    path('order_complete/', views.order_complete, name='order_complete')

]
