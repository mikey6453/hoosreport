from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate, login
from .forms import CustomUserCreationForm
import boto3
from django.conf import settings

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
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # Optionally, log the user in directly after signing up
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')  # Adjust the redirection as needed
        else:
            # Return the form with errors
            return render(request, "googleAuth/signup.html", {'form': form})
    else:
        form = CustomUserCreationForm()
    return render(request, "googleAuth/signup.html", {'form': form})

def uploads_view(request):
    return render(request, "googleAuth/uploads.html")

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Create an S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
)

@csrf_exempt
def submitted_report_view(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        file_name = file.name
        
        # Upload the file to AWS S3 bucket
        try:
            s3_client.upload_fileobj(file, 'project-b-01', file_name)
            return JsonResponse({'message': 'File uploaded successfully!'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
    return JsonResponse({'error': 'Method not allowed'}, status=405)



