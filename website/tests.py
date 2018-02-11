from unittest.mock import patch
from django.test import TestCase
from django.urls import resolve
from django.contrib.auth.models import User

# Create your tests here.
class TestIndex(TestCase):

    def test_url_resolution(self):
        resolver = resolve('/')
        self.assertEqual(resolver.view_name, 'website.views.index')

    @patch('website.views.is_authenticated')
    def test_if_signed_in_redirect_to_home_page(self, is_authenticated):
        is_authenticated.return_value = True
        response = self.client.get('/')
        self.assertRedirects(response, '/home')

    @patch('website.views.is_authenticated')
    def test_if_not_signed_in_redirect_to_welcome_page(self, is_authenticated):
        is_authenticated.return_value = False
        response = self.client.get('/')
        self.assertRedirects(response, '/welcome')

class TestWelcome(TestCase):

    def test_url_resolution(self):
        resolver = resolve('/welcome')
        self.assertEqual(resolver.view_name, 'welcome')
    
    def test_template_used(self):
        response = self.client.get('/welcome')
        self.assertTemplateUsed(response, 'website/welcome.html')

class TestHome(TestCase):

    def test_url_resolution(self):
        resolver = resolve('/home')
        self.assertEqual(resolver.view_name, 'home')
    
    def test_template_used(self):
        response = self.client.get('/home')
        self.assertTemplateUsed(response, 'website/home.html')

class TestRegistration(TestCase):

    def test_url_resolution(self):
        resolver = resolve('/register')
        self.assertEqual(resolver.view_name, 'register')
    
    def test_register_new_user(self):
        self.client.post('/register', {'email': 'voong.david@gmail.com', 'password': 'password'})
        user = User.objects.get(username='voong.david@gmail.com')
