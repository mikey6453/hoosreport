from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate, login
from django.views.decorators.http import require_POST

from .forms import CustomUserCreationForm
import boto3
import io
import uuid
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

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

# Create an S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
)


def uploads_view(request):
    bucket_name = 'project-b-01'
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    files = {}

    if 'Contents' in response:
        for obj in response['Contents']:
            file_name = obj['Key']

            if file_name.startswith('admin/') or file_name.startswith('css/') or file_name.startswith('js/'):
                continue

            # Fetch status from S3 object metadata
            metadata = s3_client.head_object(Bucket=bucket_name, Key=file_name)['Metadata']
            status = metadata.get('status', 'None')
            user_id = metadata.get('user_id', 'None')
            username = metadata.get('username', 'None')
            submission_id = metadata.get('submission_id', 'None')

            if submission_id not in files:
                files[submission_id] = []

            files[submission_id].append({
                'name': file_name,
                'status': status,
                'user_id': user_id,
                'username': username
            })

    return render(request, 'googleAuth/uploads.html', {'files': files})


@require_POST
@csrf_exempt
def submitted_report_view(request):
    if request.method == 'POST':
        submission_id = str(uuid.uuid4())  # Generate a unique submission ID

        file = request.FILES.get('file')
        text = request.POST.get('text')

        if file is not None or text:
            status = 'New'
            try:
                # Include user information if authenticated

                user_id = "None"
                username = "None"
                if request.user.is_authenticated:
                    user_id = str(request.user.id)
                    username = request.user.username

                metadata = {'status': status, 'submission_id': submission_id, 'user_id': user_id, 'username': username}

                if file:
                    # Handle file submission
                    file_name = file.name
                    s3_client.upload_fileobj(file, 'project-b-01', file_name, ExtraArgs={'Metadata': metadata})

                if text:
                    # Handle text submission
                    text_bytes = text.encode('utf-8')
                    text_file = io.BytesIO(text_bytes)
                    text_file_name = f"text_submission_{submission_id}.txt"
                    s3_client.upload_fileobj(text_file, 'project-b-01', text_file_name, ExtraArgs={'Metadata': metadata})

                return redirect('home')
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        else:
            alert_message = "No file or text provided!"
            return render(request, 'submission_error.html', {'alert_message': alert_message})
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def view_submissions(request):
    bucket_name = 'project-b-01'
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    files = {}

    if 'Contents' in response:
        for obj in response['Contents']:
            file_name = obj['Key']

            # Fetch status from S3 object metadata
            metadata = s3_client.head_object(Bucket=bucket_name, Key=file_name)['Metadata']
            status = metadata.get('status', 'None')
            user_id = metadata.get('user_id', 'None')
            username = metadata.get('username', 'None')
            submission_id = metadata.get('submission_id', 'None')

            # print(request.user.id)
            # print(request.user.username)

            # Check if the file belongs to the current user
            if user_id == str(request.user.id) and username == request.user.username:
                if submission_id not in files:
                    files[submission_id] = []

                files[submission_id].append({
                    'name': file_name,
                    'status': status,
                    'user_id': user_id,
                    'username': username
                })

    return render(request, 'googleAuth/view_submissions.html', {'files': files})


def fileview_view(request, file_name):
    """
    Generates a presigned URL for the file to be viewed directly in the browser.
    """
    # Generate the presigned URL with an inline content disposition
    file_url = s3_client.generate_presigned_url('get_object',
                                                Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                                        'Key': file_name,
                                                        'ResponseContentDisposition': 'inline'},
                                                ExpiresIn=3600)  # URL expires in 1 hour

    context = {'file_name': file_name, 'file_url': file_url}
    return render(request, 'googleAuth/fileview.html', context)