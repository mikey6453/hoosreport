from django.shortcuts import render, redirect
from django.contrib.auth import logout

def home(request):
    user = request.user
    return render(request, "googleAuth/home.html", {'user': user})

def login_view(request):
    return render(request, "googleAuth/login.html")

def logout_view(request):
    logout(request)
    # Update the URL to include your application's login URL after logging out from Google
    google_logout_url = 'https://accounts.google.com/Logout?continue=https://appengine.google.com/_ah/logout?continue=https://project-b-01-d00b72518ac8.herokuapp.com/login_view'
    return redirect(google_logout_url)



