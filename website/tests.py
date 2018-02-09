from django.test import TestCase
from django.urls import resolve

# Create your tests here.
class TestHome(TestCase):

    def test_url_resolution(self):
        resolver = resolve('/')
        self.assertEqual(resolver.view_name, 'website.views.home')
    
    def test_template_used(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'website/home.html')
