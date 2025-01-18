from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Prefetch
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import date, datetime
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D  # D is shortcut for Distance
from django.contrib.gis.db.models.functions import Distance

from accounts.models import UserProfile
from vendor.models import Vendor, OpeningHour
from menu.models import Category, FoodItem
from .models import Cart
from .context_processors import get_cart_counter, get_cart_amounts
from orders.forms import OrderForm


def marketplace(request):
    """ View for the marketplace, listing all approved and active vendors."""
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    context = {
        'vendors': vendors,
        'vendor_count': vendor_count
    }
    return render(request, "marketplace/listings.html", context)


def vendor_detail(request, vendor_slug):
    """View to display details of a specific vendor."""
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    # Fetch categories related to the vendor, along with prefetching related available food items
    # prefetch -    Reduces the number of queries to the database by fetching all related data in a single query.
    # prefetch_related is used to prefetch related objects, in this case, fooditems which is a related ForeignKey or ManyToMany field on Category.
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset=FoodItem.objects.filter(is_available=True)
        )
    )

    opening_hours = OpeningHour.objects.filter(vendor=vendor).order_by('day', '-from_hour')

    # check current day's Opening hours
    today = date.today().isoweekday()
    current_day_opening_hours = OpeningHour.objects.filter(vendor=vendor, day=today)

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    context = {
        'vendor': vendor,
        'categories': categories,
        'cart_items': cart_items,
        'opening_hours': opening_hours,
        'current_day_opening_hours': current_day_opening_hours,
    }
    return render(request, "marketplace/listing_detail.html", context)


def add_to_cart(request, food_id=None):
    """View to add a food item to the cart."""
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == "XMLHttpRequest":
            # check if food exists
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                # check user is already added food to cart
                try:
                    cart_item = Cart.objects.get(user=request.user, fooditem=fooditem)
                    cart_item.quantity += 1
                    cart_item.save()
                    return JsonResponse({'status': 'success',
                                         'message': 'Increased cart Quantity',
                                         'cart_counter': get_cart_counter(request),
                                         'qty': cart_item.quantity,
                                         'cart_amount': get_cart_amounts(request)
                                         })
                except:
                    cart_item = Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)
                    return JsonResponse({'status': 'success',
                                         'message': 'Added Food to Cart',
                                         'cart_counter': get_cart_counter(request),
                                         'qty': cart_item.quantity,
                                         'cart_amount': get_cart_amounts(request)
                                         })
            except:
                return JsonResponse({
                    'status': 'failed',
                    'message': 'This Food Does not exist'
                })
        else:
            return JsonResponse({
                'status': 'failed',
                'message': 'Invalid request'
            })
    else:
        return JsonResponse({
            'status': 'login_required',
            'message': 'Please Login To Continue'
        })


def decrease_cart(request, food_id=None):
    """View to decrease the quantity of a food item in the cart."""
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == "XMLHttpRequest":
            # check if food exists
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                # check if user has already added food to the cart
                try:
                    cart_item = Cart.objects.get(user=request.user, fooditem=fooditem)
                    if cart_item.quantity >= 1:
                        # decrease quantity
                        cart_item.quantity -= 1
                        cart_item.save()
                    else:
                        cart_item.delete()
                        cart_item.quantity = 0
                    return JsonResponse({
                        'status': 'success',
                        'cart_counter': get_cart_counter(request),
                        'qty': cart_item.quantity,
                        'cart_amount': get_cart_amounts(request)
                    })
                except:
                    Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)
                    return JsonResponse({
                        'status': 'failed',
                        'message': 'You do not have this item in your cart'
                    })
            except:
                return JsonResponse({
                    'status': 'failed',
                    'message': 'This Food Does not exist'
                })
        else:
            return JsonResponse({
                'status': 'failed',
                'message': 'Invalid request'
            })
    else:
        return JsonResponse({
            'status': 'login_required',
            'message': 'Please Login To Continue'
        })


@login_required(login_url='login')
def cart(request):
    """ View to display the user's cart."""
    cartitems = Cart.objects.filter(user=request.user).order_by('created_at')
    context = {
        'cartitems': cartitems
    }
    return render(request, "marketplace/cart.html", context)


def delete_cart(request, cart_id=None):
    """View to delete an item from the cart."""
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == "XMLHttpRequest":
            try:
                cartitem = Cart.objects.get(user=request.user, id=cart_id)
                if cartitem:
                    cartitem.delete()
                    return JsonResponse({
                        'status': 'Success',
                        'message': 'Cart Item Deleted Successfully',
                        'cart_counter': get_cart_counter(request),
                        'cart_amount': get_cart_amounts(request)
                    })
            except:
                return JsonResponse({
                    'status': 'failed',
                    'message': 'Cart Item does not Exist'
                })
        else:
            return JsonResponse({
                'status': 'failed', 'message': 'Invalid Request'
            })


def search(request):
    """Search for vendors based on user-provided address, latitude, longitude, keyword, and radius."""
    if 'address' not in request.GET:
        return redirect('marketplace')
    else:
        address = request.GET['address']
        latitude = request.GET['lat']
        longitude = request.GET['lng']
        keyword = request.GET['keyword']
        radius = request.GET['radius']

        # Retrieve vendor IDs that offer the specified food item requested by the user
        # extracts the vendor IDs associated with these FoodItem records & returns them as a flat list instead of a list of tuples.
        fetch_vendors_by_fooditems = FoodItem.objects.filter(food_title__icontains=keyword,
                                                             is_available=True).values_list('vendor', flat=True)

        vendors = Vendor.objects.filter(
            Q(id__in=fetch_vendors_by_fooditems) | Q(vendor_name__icontains=keyword, is_approved=True,
                                                     user__is_active=True))
        if latitude and longitude and radius:
            pnt = GEOSGeometry(f'POINT({longitude} {latitude})')
            vendors = Vendor.objects.filter(
                Q(id__in=fetch_vendors_by_fooditems) | Q(vendor_name__icontains=keyword, is_approved=True,
                                                         user__is_active=True),
                user_profile__location__distance_lte=(pnt, D(km=radius))).annotate(
                distance=Distance("user_profile__location", pnt)).order_by("distance")
            for v in vendors:
                v.kms = round(v.distance.km, 1)
        vendor_count = vendors.count()

        context = {
            'vendors': vendors,
            'vendor_count': vendor_count,
            'source_location': address
        }
        return render(request, "marketplace/listings.html", context)


def checkout(request):
    """Display the checkout form pre-filled with the user's profile information."""
    cartitems = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cartitems.count()
    if cart_count <= 0:
        return redirect('marketplace')
    user_profile = UserProfile.objects.get(user=request.user)
    default_values = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'phone': request.user.phone_number,
        'email': request.user.email,
        'address': user_profile.address,
        'country': user_profile.country,
        'state': user_profile.state,
        'city': user_profile.city,
        'pin_code': user_profile.pincode,
    }
    form = OrderForm(initial=default_values)
    context = {
        'form': form,
        'cartitems': cartitems
    }
    return render(request, "marketplace/checkout.html", context)
