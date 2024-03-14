from django.urls import path 
from . import views

urlpatterns = [
    path("", views.home),
    path("logout", views.logout_view),
    path("login", views.login_view),
    path("signup", views.signup_view),
    path("submit_report", views.report_view, name='submit_report')
]