from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages

from .forms import UserForm
from .models import User


# def registerUser(request):
#     return HttpResponse("<h1>This is Test register</h1>")


def registerUser(request):
    if request.method == "POST":
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
