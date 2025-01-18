"""
URL configuration for CuisionSynergy_main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views
from marketplace import views as MarketPlaceViews

urlpatterns = [
                    # Admin panel route
                    path('admin/', admin.site.urls),

                    # Home page route
                    path('', views.home, name='home'),

                    # about-us page
                    path('about-us/', views.about_us, name='about-us'),

                    # careers page
                    path('career/', views.career, name='career'),

                    # press-releases page
                    path('press/', views.press, name='press'),

                    # blog page
                    path('blogs/', views.blogs, name='blogs'),

                    # terms and conditions page
                    path('terms_conditions/', views.terms_conditions, name='terms_conditions'),

                    # privacy-policy page
                    path('privacy_policy/', views.privacy_policy, name='privacy_policy'),

                    # cookie policy page
                    path('cookie_policy/', views.cookie_policy, name='cookie_policy'),

                    # Include the 'accounts' app's URLs
                    path('', include('accounts.urls')),

                    # Marketplace-related routes
                    path('marketplace/', include('marketplace.urls')),

                    # Orders-related routes
                    path('orders/',include('orders.urls')),

                    # Cart page route
                    path('cart/', MarketPlaceViews.cart, name='cart'),

                    # Search functionality route
                    path('search/', MarketPlaceViews.search, name='search'),

                    # Checkout page route
                    path('checkout/', MarketPlaceViews.checkout, name='checkout'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Static file handling (media files)

