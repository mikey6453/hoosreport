from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name='home'),
    path("logout/", views.logout_view, name='logout'),
    path("login/", views.login_view, name='login'),
    path("signup/", views.signup_view, name='signup'),
    path("submit_report/", views.report_view, name='submit_report'),
    path("uploads/", views.uploads_view, name="uploads"),
]
