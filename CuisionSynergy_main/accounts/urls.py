from django.urls import path, include

from . import views

urlpatterns = [
    # Base path for the account management view
    path('', views.my_account),

    # Registration routes for users and vendors
    path('registerUser/', views.registerUser, name='registerUser'),
    path('registerVendor/', views.registerVendor, name='registerVendor'),

    # Authentication routes
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),

    # Account and dashboard routes
    path('my_account/', views.my_account, name='my_account'),
    path('customer_dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('vendor_dashboard/', views.vendor_dashboard, name='vendor_dashboard'),

    # Account activation routes
    path('activate/<uid64>/<token>/', views.activate, name='activate'),

    # Password reset routes
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset_password_validate/<uid64>/<token>/', views.reset_password_validate, name='reset_password_validate'),
    path('reset_password/', views.reset_password, name='reset_password'),

    # Including additional URL configurations from vendor and customer apps
    path('vendor/', include('vendor.urls')),
    path('customer/', include('customers.urls'))

]
