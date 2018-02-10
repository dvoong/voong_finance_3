from unittest import mock
from django.test import TestCase
from django.urls import resolve

# Create your tests here.
class TestHome(TestCase):

    def test_url_resolution(self):
        resolver = resolve('/')
        self.assertEqual(resolver.view_name, 'website.views.index')
    
    def test_template_used(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'website/welcome.html')

    @mock...
    def test_if_not_signed_in_redirect_to_welcome_page(self, is_authenticated):
        is_authenticated.returns False
        response = self.client.get('/')
        self.assertRedirects(response, '/welcome')
