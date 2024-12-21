from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required

from vendor.models import Vendor
from menu.models import Category, FoodItem
from .models import Cart
from .context_processors import get_cart_counter, get_cart_amounts


def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    context = {
        'vendors': vendors,
        'vendor_count': vendor_count
    }
    return render(request, "marketplace/listings.html", context)


def vendor_detail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset=FoodItem.objects.filter(is_available=True)
        )
    )
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    context = {
        'vendor': vendor,
        'categories': categories,
        'cart_items': cart_items
    }
    return render(request, "marketplace/listing_detail.html", context)


def add_to_cart(request, food_id=None):
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
    cartitems = Cart.objects.filter(user=request.user).order_by('created_at')
    context = {
        'cartitems': cartitems
    }
    return render(request, "marketplace/cart.html", context)


def delete_cart(request, cart_id=None):
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
