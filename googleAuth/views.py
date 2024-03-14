from django.shortcuts import render, redirect
from django.contrib.auth import logout

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
    return render(request, "googleAuth/login.html")

def logout_view(request):
    logout(request)
    return render(request, "googleAuth/signedout.html")



