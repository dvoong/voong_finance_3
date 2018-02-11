from unittest.mock import patch
from django.test import TestCase
from django.urls import resolve

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

