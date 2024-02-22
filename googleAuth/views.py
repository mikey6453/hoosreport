from django.shortcuts import render, redirect
from django.contrib.auth import logout

def home(request):
    return render(request, "googleAuth/home.html")

def login_view(request):
    return render(request, "googleAuth/login.html")

def logout_view(request):
    logout(request)
    return redirect("/")



