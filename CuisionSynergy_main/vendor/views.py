from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.defaultfilters import slugify
from django.http import HttpResponse, JsonResponse

from .forms import VendorForm, OpeningHourForm
from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from .models import Vendor, OpeningHour
from accounts.views import check_role_vendor
from menu.models import Category, FoodItem
from menu.forms import CategoryForm, FoodItemForm
from orders.models import Order, OrderedFood


def get_vendor(request):
    """Retrieve the Vendor instance associated with the current user."""
    return Vendor.objects.get(user=request.user)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vprofile(request):
    """View to display and update vendor profile and user profile information."""
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    if request.method == "POST":
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)
        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, "Settings Updated")
            return redirect('vprofile')
        else:
            print(profile_form.errors)
            print(vendor_form.errors)
    else:
        profile_form = UserProfileForm(instance=profile)
        vendor_form = VendorForm(instance=vendor)
    context = {
        'profile_form': profile_form,
        'vendor_form': vendor_form,
        'profile': profile,
        'vendor': vendor
    }
    return render(request, "vendor/vprofile.html", context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def menu_builder(request):
    """View to display the menu builder with categories for the current vendor."""
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor=vendor).order_by('created_at')
    context = {
        'category': categories,
    }
    return render(request, 'vendor/menu_builder.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def fooditems_by_category(request, pk):
    """View to display food items by category for the current vendor."""
    vendor = get_vendor(request)
    categories = get_object_or_404(Category, pk=pk)
    food_items = FoodItem.objects.filter(vendor=vendor, category=categories)
    context = {
        'category': categories,
        'food_items': food_items
    }
    return render(request, 'vendor/fooditems_category.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_category(request):
    """View to add a new category for the current vendor."""
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.save()
            category.slug = slugify(category_name) + "-" + str(category.id)
            category.save()
            messages.success(request, 'category Created Successfully')
            return redirect('menu_builder')
        else:
            print(form.errors)
    else:
        form = CategoryForm()
    context = {
        'form': form
    }
    return render(request, 'vendor/add_category.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_category(request, pk=None):
    """View to edit an existing category for the current vendor."""
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            form.save()
            messages.success(request, 'category Updated Successfully')
            return redirect('menu_builder')
        else:
            print(form.errors)
    else:
        form = CategoryForm(instance=category)
    context = {
        'form': form,
        'category': category
    }
    return render(request, 'vendor/edit_category.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_category(request, pk=None):
    """View to delete an existing category for the current vendor."""
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, "Category has been deleted Successfully")
    return redirect('menu_builder')


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_food(request):
    """View to add a new food item for the current vendor."""
    if request.method == "POST":
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(food_title)
            form.save()
            messages.success(request, "Food Item Created Successfully")
            return redirect('fooditems_by_category', food.category.id)
        else:
            print(form.errors)
    else:
        form = FoodItemForm()
        # modify to show category only for logged in vendors
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    context = {
        'form': form
    }
    return render(request, 'vendor/add_food.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_food(request, pk=None):
    """View to edit an existing food item for the current vendor."""
    food = get_object_or_404(FoodItem, pk=pk)
    if request.method == "POST":
        form = FoodItemForm(request.POST, request.FILES, instance=food)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(food_title)
            form.save()
            messages.success(request, 'FoodItem Updated Successfully')
            return redirect('fooditems_by_category', food.category.id)
        else:
            print(form.errors)
    else:
        form = FoodItemForm(instance=food)
        # modify to show category only for logged in vendors
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    context = {
        'form': form,
        'food': food
    }
    return render(request, "vendor/edit_food.html", context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_food(request, pk):
    """View to delete an existing food item for the current vendor."""
    food = get_object_or_404(FoodItem, pk=pk)
    food.delete()
    messages.success(request, "Food has been deleted Successfully")
    return redirect('fooditems_by_category', food.category.id)


def opening_hour(request):
    """Display the opening hours for the current vendor."""
    opening_hours = OpeningHour.objects.filter(vendor=get_vendor(request))
    form = OpeningHourForm()
    context = {
        'form': form,
        'opening_hours': opening_hours
    }
    return render(request, "vendor/opening_hour.html", context)


def opening_hour_add(request):
    """Add a new opening hour for the current vendor via an AJAX request."""
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == "XMLHttpRequest" and request.method == "POST":
            day = request.POST['day']
            from_hour = request.POST['from_hour']
            to_hour = request.POST['to_hour']
            is_closed = request.POST['is_closed']
            try:
                hour = OpeningHour.objects.create(vendor=get_vendor(request), day=day, from_hour=from_hour,
                                                  to_hour=to_hour, is_closed=is_closed)
                if hour:
                    day = OpeningHour.objects.get(id=hour.id)
                    if day.is_closed:
                        response = {'status': 'success', 'id': hour.id, 'day': day.get_day_display(),
                                    'is_closed': 'Closed'}
                    else:
                        response = {'status': 'success', 'id': hour.id, 'day': day.get_day_display(),
                                    'from_hour': hour.from_hour, 'to_hour': hour.to_hour}
                return JsonResponse(response)
            except IntegrityError as e:
                response = {'status': 'failed', 'message': from_hour + '-' + to_hour + ' already exists for this day!'}
                return JsonResponse(response)
        else:
            HttpResponse('Invalid request')


def remove_opening_hour(request, pk):
    """Remove an existing opening hour for the current vendor via an AJAX request."""
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            hour = get_object_or_404(OpeningHour, pk=pk)
            hour.delete()
            return JsonResponse({'status': 'success', 'id': pk})


def order_detail(request, order_number):
    """Display the details of a specific order for the current vendor."""
    order = Order.objects.get(order_number=order_number, is_ordered=True)
    ordered_food = OrderedFood.objects.filter(order=order, fooditem__vendor=get_vendor(request))
    context = {
        'order': order,
        'ordered_food': ordered_food,
        'subtotal': order.get_total_by_vendor()['subtotal'],
        'taxdata': order.get_total_by_vendor()['tax_data'],
        'grand_total': order.get_total_by_vendor()['grand_total']
    }
    return render(request, "vendor/order_detail.html", context)


def my_orders(request):
    """Display all the orders for the current vendor."""
    vendor = Vendor.objects.get(user=request.user)
    orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders
    }
    return render(request, "vendor/my_orders.html", context)
