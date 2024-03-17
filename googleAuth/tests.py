from django.test import TestCase

# Create your tests here.

from django.test import TestCase
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm

class CustomUserCreationFormTest(TestCase):

    def test_form_success(self):
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_fail_on_duplicate_email(self):
        User.objects.create_user('testuser', 'test@example.com', 'testpassword123')
        form_data = {
            'username': 'anotheruser',
            'email': 'test@example.com', # Duplicate email
            'password1': 'testpassword123',
            'password2': 'testpassword123',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_form_fail_on_duplicate_username(self):
        User.objects.create_user('testuser', 'test@example.com', 'testpassword123')
        form_data = {
            'username': 'testuser', # Duplicate username
            'email': 'anotheremail@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
