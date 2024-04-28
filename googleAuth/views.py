from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate, login
from django.views.decorators.http import require_POST
import mimetypes

from .forms import CustomUserCreationForm
import boto3
import io
import uuid
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from botocore.exceptions import ClientError
import json

# Initialize the S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)


def home(request):
    user = request.user

    if not request.session.get("warning_shown", False):
        request.session["warning_shown"] = True
        show_warning = True
    else:
        show_warning = False

    context = {
        "user": user,
        "show_warning": show_warning,
    }
    return render(request, "googleAuth/home.html", context)


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            return render(
                request,
                "socialaccount/login.html",
                {"error": "Invalid username or password."},
            )
    return render(request, "socialaccount/login.html")


def logout_view(request):
    logout(request)
    return render(request, "googleAuth/signedout.html")


def report_view(request):
    return render(request, "googleAuth/report.html")


def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # Optionally, log the user in directly after signing up
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect("home")  # Adjust the redirection as needed
        else:
            # Return the form with errors
            return render(request, "googleAuth/signup.html", {"form": form})
    else:
        form = CustomUserCreationForm()
    return render(request, "googleAuth/signup.html", {"form": form})


# Create an S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)


def uploads_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("home")
    bucket_name = "project-b-01"
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    files = {}

    if "Contents" in response:
        for obj in response["Contents"]:
            file_name = obj["Key"]

            if (
                file_name.startswith("admin/")
                or file_name.startswith("css/")
                or file_name.startswith("js/")
                or file_name.startswith("comment")
            ):
                continue

            # Disallow other file types
            if not (
                file_name.endswith(".pdf")
                or file_name.endswith(".txt")
                or file_name.endswith(".jpg")
            ):
                continue

            # Fetch status from S3 object metadata
            metadata = s3_client.head_object(Bucket=bucket_name, Key=file_name)[
                "Metadata"
            ]
            status = metadata.get("status", "None")
            user_id = metadata.get("user_id", "None")
            username = metadata.get("username", "None")
            submission_id = metadata.get("submission_id", "None")

            if submission_id not in files:
                files[submission_id] = []

            files[submission_id].append(
                {
                    "name": file_name,
                    "status": status,
                    "user_id": user_id,
                    "username": username,
                }
            )

    return render(request, "googleAuth/uploads.html", {"files": files})


def thank_you_view(request):
    return render(request, "googleAuth/thank_you.html")


@require_POST
@csrf_exempt
def submitted_report_view(request):
    if request.method == "POST":
        submission_id = str(uuid.uuid4())  # Generate a unique submission ID

        file = request.FILES.get("file")
        text = request.POST.get("text")

        if file is not None or text:
            status = "New"
            try:
                # Include user information if authenticated

                user_id = "None"
                username = "None"
                if request.user.is_authenticated:
                    user_id = str(request.user.id)
                    username = request.user.username

                metadata = {
                    "status": status,
                    "submission_id": submission_id,
                    "user_id": user_id,
                    "username": username,
                }

                if file:
                    # Handle file submission
                    file_name = file.name
                    s3_client.upload_fileobj(
                        file,
                        "project-b-01",
                        file_name,
                        ExtraArgs={"Metadata": metadata},
                    )

                if text:
                    # Handle text submission
                    text_bytes = text.encode("utf-8")
                    text_file = io.BytesIO(text_bytes)
                    text_file_name = f"text_submission_{submission_id}.txt"
                    s3_client.upload_fileobj(
                        text_file,
                        "project-b-01",
                        text_file_name,
                        ExtraArgs={"Metadata": metadata},
                    )

                return redirect("thank_you")
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)
        else:
            alert_message = "No file or text provided!"
            return render(
                request, "submission_error.html", {"alert_message": alert_message}
            )
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)


@login_required
def view_submissions(request):
    if not request.user.is_authenticated:
        return redirect("home")
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        bucket_name = "project-b-01"
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        files = {}

        if "Contents" in response:
            for obj in response["Contents"]:
                file_name = obj["Key"]
                metadata = s3_client.head_object(Bucket=bucket_name, Key=file_name)[
                    "Metadata"
                ]
                status = metadata.get("status", "None")
                user_id = metadata.get("user_id", "None")
                username = metadata.get("username", "None")
                submission_id = metadata.get("submission_id", "None")

                if (
                    user_id == str(request.user.id)
                    and username == request.user.username
                ):
                    if submission_id not in files:
                        files[submission_id] = []

                    files[submission_id].append(
                        {
                            "name": file_name,
                            "status": status,
                            "user_id": user_id,
                            "username": username,
                        }
                    )

        return JsonResponse(files)

    # Return the initial page template if it's not an AJAX request
    return render(request, "googleAuth/view_submissions.html")


def fileview_view(request, file_name):
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    try:
        metadata = s3_client.head_object(Bucket=bucket_name, Key=file_name)["Metadata"]
        submission_id = metadata.get("submission_id")
        if submission_id:
            comment_file_name = f"comment_{submission_id}.txt"
        else:
            return HttpResponse("Submission ID not found.", status=404)
    except ClientError:
        return HttpResponse("Error fetching file metadata.", status=500)

    status = metadata.get("status", "None")

    if status == "New" and request.user.is_authenticated:
        if request.user.is_superuser:
            metadata["status"] = "In-progress"
        try:
            s3_client.copy_object(
                Bucket=bucket_name,
                CopySource={"Bucket": bucket_name, "Key": file_name},
                Key=file_name,
                Metadata=metadata,
                MetadataDirective="REPLACE",
            )
        except ClientError as e:
            print(f"Error updating file status: {e}")

    if request.method == "POST":
        text = request.POST.get("text")
        metadata["status"] = "Resolved"
        try:
            s3_client.put_object(
                Bucket=bucket_name,
                Key=comment_file_name,
                Body=text,
                ContentType="text/plain",
            )
            s3_client.copy_object(
                Bucket=bucket_name,
                CopySource={"Bucket": bucket_name, "Key": file_name},
                Key=file_name,
                Metadata=metadata,
                MetadataDirective="REPLACE",
            )
        except ClientError as e:
            print(f"Error uploading comment file: {e}")

    display_comment = None
    try:
        comment_object = s3_client.get_object(Bucket=bucket_name, Key=comment_file_name)
        display_comment = comment_object["Body"].read().decode("utf-8")
    except ClientError:
        pass

    file_url = generate_presigned_url(bucket_name, file_name)

    context = {
        "file_name": file_name,
        "file_url": file_url,
        "display_comment": display_comment,
        "status": metadata["status"],
    }

    return render(request, "googleAuth/fileview.html", context)


def generate_presigned_url(bucket_name, file_name):
    try:
        return s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": bucket_name,
                "Key": file_name,
            },
            ExpiresIn=3600,
        )
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        return None


def submit_comment_view(request, submission_id):
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    comment_file_name = f"comment_{submission_id}.txt"

    if request.method == "POST":
        comment_text = request.POST.get("text")
        if comment_text:
            comment_bytes = comment_text.encode("utf-8")
            comment_file = io.BytesIO(comment_bytes)
            comment_file_name = f"resolved_{comment_file_name}.txt"

            try:
                s3_client.upload_fileobj(
                    comment_file,
                    bucket_name,
                    comment_file_name,
                    ExtraArgs={"ContentType": "text/plain"},
                )
            except Exception as e:
                print(f"Error uploading comment file: {e}")
                return HttpResponse("Error in saving the comment.", status=500)
            return redirect("uploads")
        else:
            return HttpResponse("No comment provided.", status=400)

    return render(
        request, "path/to/comment_form.html", {"file_name": comment_file_name}
    )
