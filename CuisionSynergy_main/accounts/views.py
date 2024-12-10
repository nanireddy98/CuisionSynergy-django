from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied

from .forms import UserForm
from vendor.forms import VendorForm
from .models import User, UserProfile
from .utils import detectUser


# def registerUser(request):
#     return HttpResponse("<h1>This is Test register</h1>")


# restrict vendor from accessing customer Dashboard
def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied


# restrict vendor from accessing customer Dashboard
def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied


def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, "You already LoggedIn!")
        return redirect('my_account')
    elif request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            """ Create user using form"""
            # password = form.cleaned_data['password']
            # user = form.save(commit=False)
            # user.role = User.CUSTOMER
            # user.set_password(password)
            # user.save()
            # return redirect('registerUser')
            """ Create user using create_user method"""
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username,
                                            password=password)
            user.role = User.CUSTOMER
            user.save()
            messages.success(request, "Your account has been Registered Successfully")
            return redirect('registerUser')
    else:
        form = UserForm()
    context = {
        'form': form
    }
    return render(request, 'accounts/registerUser.html', context)


def registerVendor(request):
    if request.user.is_authenticated:
        messages.warning(request, "You already LoggedIn!")
        return redirect('my_account')
    elif request.method == "POST":
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and v_form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username,
                                            password=password)
            user.role = User.VENDOR
            user.save()
            vendor = v_form.save(commit=False)
            vendor.user = user
            vendor.user_profile = UserProfile.objects.get(user=user)
            vendor.save()
            messages.success(request, "Your account has been Registered Successfully.\nPlease Wait for Approval")
            return redirect('registerVendor')
        else:
            print("Invalid form")
            print(form.errors)
    else:
        form = UserForm()
        v_form = VendorForm()
    context = {
        'form': form,
        'v_form': v_form
    }
    return render(request, "accounts/registerVendor.html", context)


def login(request):
    if request.user.is_authenticated:
        messages.warning(request, "You already LoggedIn!")
        return redirect('my_account')
    elif request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            auth.login(request, user)
            messages.success(request, "You are Logged In!")
            return redirect('my_account')
        else:
            messages.error(request, "Invalid Credentials")
            return redirect('login')

    return render(request, 'accounts/login.html')


def logout(request):
    auth.logout(request)
    messages.info(request, "You are LoggedOut!")
    return redirect('login')


@login_required(login_url=login)
def my_account(request):
    user = request.user
    redirectUrl = detectUser(user)
    return redirect(redirectUrl)


@login_required(login_url=login)
@user_passes_test(check_role_customer)
def customer_dashboard(request):
    return render(request, 'accounts/customer_dashboard.html')


@login_required(login_url=login)
@user_passes_test(check_role_vendor)
def vendor_dashboard(request):
    return render(request, 'accounts/vendor_dashboard.html')
