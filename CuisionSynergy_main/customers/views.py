import json

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounts.forms import UserInfoForm, UserProfileForm
from accounts.models import UserProfile
from orders.models import Order, OrderedFood


@login_required(login_url='login')
def cprofile(request):
    """
    Handles the customer profile view.
    Displays the profile and allows the user to update their profile information.
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST":
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserInfoForm(request.POST, instance=request.user)
        if profile_form.is_valid() and user_form.is_valid():
            # Save the forms if they are valid
            profile_form.save()
            user_form.save()
            messages.success(request, "Profile Updated Successfully")
            return redirect('cprofile')
        else:
            # Print form errors if any
            print(profile_form.errors)
            print(user_form.errors)
    else:
        # Instantiate forms with the current profile and user data
        profile_form = UserProfileForm(instance=profile)
        user_form = UserInfoForm(instance=request.user)
    context = {
        'profile_form': profile_form,
        'user_form': user_form,
        'profile': profile
    }
    return render(request, "customers/cprofile.html", context)


def my_orders(request):
    """Displays a list of the customer's orders."""
    orders = Order.objects.filter(user=request.user, is_ordered=True)
    context = {
        'orders': orders
    }
    return render(request, "customers/my_orders.html", context)


def order_detail(request, order_number):
    """Displays the details of a specific order."""
    try:
        # Retrieve the order and related ordered food items
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order)
        subtotal = 0

        # Calculate the subtotal of the ordered food items
        for item in ordered_food:
            subtotal += (item.price * item.quantity)

        # Parse the tax data from the order
        taxdata = json.loads(order.tax_data)
        context = {
            'order': order,
            'ordered_food': ordered_food,
            'taxdata': taxdata,
            'subtotal': subtotal
        }
    except:
        # Redirect to the customer dashboard if an error occurs
        return redirect('customer')
    return render(request, "customers/order_detail.html", context)
