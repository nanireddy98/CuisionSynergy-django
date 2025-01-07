import datetime

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.template.defaultfilters import slugify

from .forms import UserForm
from vendor.forms import VendorForm
from .models import User, UserProfile
from .utils import detectUser, send_verification_mail
from orders.models import Order
from vendor.models import Vendor


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

            # send verification mail
            mail_subject = "Activate Your Account"
            email_template = "accounts/emails/account_verification_email.html"
            send_verification_mail(request, user, mail_subject, email_template)

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
            vendor_name = v_form.cleaned_data['vendor_name']
            vendor.vendor_slug = slugify(vendor_name) + "-" + str(user.id)
            vendor.user_profile = UserProfile.objects.get(user=user)
            vendor.save()

            # send verification mail
            mail_subject = "Activate Your Account"
            email_template = "accounts/emails/account_verification_email.html"
            send_verification_mail(request, user, mail_subject, email_template)

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


def activate(request, uid64, token):
    try:
        uid = urlsafe_base64_decode(uid64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulations! Your account is Activated.")
        return redirect('my_account')
    else:
        messages.error(request, "Invalid activation link")
        return redirect('my_account')


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
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    recent_orders = orders[:5]
    context = {
        'orders': orders,
        'orders_count': orders.count(),
        'recent_orders': recent_orders
    }
    return render(request, 'accounts/customer_dashboard.html', context)


@login_required(login_url=login)
@user_passes_test(check_role_vendor)
def vendor_dashboard(request):
    vendor = Vendor.objects.get(user=request.user)
    orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by('-created_at')
    recent_orders = orders[:5]

    # total month's Revenue
    current_month = datetime.datetime.now().month
    current_month_orders = orders.filter(vendors__in=[vendor.id], created_at__month=current_month)
    current_month_revenue = 0
    for i in current_month_orders:
        current_month_revenue += i.get_total_by_vendor()['grand_total']

    # total revenue
    total_revenue = 0
    for i in orders:
        total_revenue += i.get_total_by_vendor()['grand_total']

    context = {
        'orders': orders,
        'orders_count': orders.count(),
        'recent_orders': recent_orders,
        'total_revenue': total_revenue,
        'current_month_revenue': current_month_revenue
    }
    return render(request, 'accounts/vendor_dashboard.html', context)


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            # send reset password link
            mail_subject = "Reset Password"
            email_template = "accounts/emails/reset_password_email.html"
            send_verification_mail(request, user, mail_subject, email_template)
            messages.success(request, "Password reset link has been sent to your email address")
            return redirect('login')
        else:
            messages.error(request, "Account Does not Exist")
            return redirect('forgot_password')
    return render(request, "accounts/forgot_password.html")


def reset_password_validate(request, uid64, token):
    try:
        uid = urlsafe_base64_decode(uid64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        # Store the user's unique identifier (uid) in the session for persistent user tracking during their session.
        request.session['uid'] = uid
        messages.info(request, "reset Password has been sent to Your Email address")
        return redirect('reset_password')
    else:
        messages.error(request, "The link has been expired")
        return redirect('my_account')


def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.save()
            messages.success(request, "Password Reset Successful")
            return redirect('login')
        else:
            messages.error(request, "Password Do not match")
            return redirect('reset_password')
    return render(request, "accounts/reset_password.html")
