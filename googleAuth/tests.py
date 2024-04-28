from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .forms import CustomUserCreationForm
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site


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
            'email': 'test@example.com',  # Duplicate email
            'password1': 'testpassword123',
            'password2': 'testpassword123',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_form_fail_on_duplicate_username(self):
        User.objects.create_user('testuser', 'test@example.com', 'testpassword123')
        form_data = {
            'username': 'testuser',  # Duplicate username
            'email': 'anotheremail@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

class SignupPageTests(TestCase):

    def setUp(self):
        site = Site.objects.get_current()
        social_app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id='test-client-id',
            secret='test-secret',
            key=''
        )
        social_app.sites.add(site)

    def test_signup_page_loads_correctly(self):
        """The signup page loads correctly."""
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'googleAuth/signup.html')
        self.assertIsInstance(response.context['form'], CustomUserCreationForm)

    def test_signup_form_error(self):
        """The signup form shows appropriate errors for invalid data."""
        response = self.client.post(reverse('signup'), data={
            'username': '',  # Missing username should trigger form error
            'email': 'user@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
        })
        self.assertTrue('form' in response.context)  
        form = response.context['form']  

        self.assertTrue(form.is_bound)  
        self.assertFalse(form.is_valid())  
        self.assertIn('username', form.errors)  

        self.assertFormError(form, 'username', 'This field is required.')
 


    def test_signup_success(self):
        """A new user is created successfully through the signup form."""
        response = self.client.post(reverse('signup'), data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
        })
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().username, 'newuser')
        self.assertTrue(User.objects.first().check_password('testpassword123'))
        self.assertRedirects(response, expected_url=reverse('home'), status_code=302, target_status_code=200)

class UserSessionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='password123')

    def test_login_view_post(self):
        """Test the login view with POST method."""
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'password123'})
        self.assertRedirects(response, reverse('home'))

    def test_logout_view(self):
        """Test the logout functionality."""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('logout'))
        self.assertFalse(response.context['user'].is_authenticated)
