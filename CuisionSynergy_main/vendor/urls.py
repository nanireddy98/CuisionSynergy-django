from django.urls import path

from . import views
from accounts import views as AccountViews

urlpatterns = [
    path('', AccountViews.vendor_dashboard),
    path('profile/', views.vprofile, name='vprofile'),
    path('menu_builder/', views.menu_builder, name='menu_builder'),
    path('menu_builder/category/<int:pk>/', views.fooditems_by_category, name='fooditems_by_category'),

    # category CRUD
    path('menu_builder/category/add/', views.add_category, name='add_category'),
    path('menu_builder/category/edit/<int:pk>/', views.edit_category, name='edit_category'),
    path('menu_builder/category/delete/<int:pk>/', views.delete_category, name='delete_category'),

    # Food CRUD
    path('menu_builder/food/add/', views.add_food, name='add_food'),
    path('menu_builder/food/edit/<int:pk>/', views.edit_food, name='edit_food'),
    path('menu_builder/food/delete/<int:pk>/', views.delete_food, name='delete_food'),

    # opening hours
    path('opening-hour', views.opening_hour, name='opening-hour'),
    path('opening-hour/add', views.opening_hour_add, name='opening-hour-add'),
    path('opening-hour/remove/<int:pk>/', views.remove_opening_hour, name='remove_opening_hour'),

    # received orders by vendor(which customers ordered)
    path('order_detail/<int:order_number>/', views.order_detail, name='vendor_order_detail'),
    path('my_orders/', views.my_orders, name='vendor_my_orders'),
]
