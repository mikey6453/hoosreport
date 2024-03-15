from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate, login
from django.http import HttpResponseRedirect

def home(request):
    user = request.user
    
    if not request.session.get('warning_shown', False):
        request.session['warning_shown'] = True
        show_warning = True
    else:
        show_warning = False
        
    context = {
        'user': user,
        'show_warning': show_warning,
    }
    return render(request, "googleAuth/home.html", context)

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, "socialaccount/login.html", {'error': 'Invalid username or password.'})
    return render(request, "socialaccount/login.html")

def logout_view(request):
    logout(request)
    return render(request, "googleAuth/signedout.html")

def report_view(request):
    return render(request, "googleAuth/report.html")

def signup_view(request):
    return render(request, "socialaccount/signup.html")

