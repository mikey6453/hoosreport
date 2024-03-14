from django.shortcuts import render, redirect
from django.contrib.auth import logout

def home(request):
    user = request.user
    return render(request, "googleAuth/home.html", {'user': user})

def login_view(request):
    return render(request, "socialaccount/login.html")

def logout_view(request):
    logout(request)
    return render(request, "googleAuth/signedout.html")

def report_view(request):
    return render(request, "googleAuth/report.html")

def signup_view(request):
    return render(request, "socialaccount/signup.html")

