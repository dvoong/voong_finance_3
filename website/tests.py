import datetime
from unittest.mock import patch
from django.test import TestCase
from django.urls import resolve
from django.contrib.auth.models import User
from website.models import Transaction

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

class TestLogin(TestCase):

    def setUp(self):
        User.objects.create_user(username='voong.david@gmail.com', email='voong.david@gmail.com', password='password')
    
    def test_rul_resolution(self):
        resolver = resolve('/login')
        self.assertEqual(resolver.view_name, 'login')

    def test_if_valid_credentials_redirects_to_home_page(self):
        response = self.client.post('/login', {'email': 'voong.david@gmail.com', 'password': 'password'})
        self.assertRedirects(response, '/home')

    def test_if_invalid_credentials_redirects_to_welcome_page(self):
        response = self.client.post('/login', {'email': 'voong.david@gmail.com', 'password': 'asdf'})
        self.assertRedirects(response, '/welcome')

# Create your tests here.
class TestIndex(TestCase):

    def test_url_resolution(self):
        resolver = resolve('/')
        self.assertEqual(resolver.view_name, 'website.views.index')

    def test_if_signed_in_redirect_to_home_page(self):
        user = User.objects.create_user(username='voong.david@gmail.com', email='voong.david@gmail.com', password='password')
        self.client.login(username='voong.david@gmail.com', password='password')
        response = self.client.get('/')
        self.assertRedirects(response, '/home')

    def test_if_not_signed_in_redirect_to_welcome_page(self):
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
        user = User.objects.create_user(username='voong.david@gmail.com', email='voong.david@gmail.com', password='password')
        self.client.login(username='voong.david@gmail.com', password='password')
        response = self.client.get('/home')
        self.assertTemplateUsed(response, 'website/home.html')

    def test_populates_transactions_list(self):
        today = datetime.date.today()
        user1 = User.objects.create_user(username='voong.david@gmail.com', password='password')
        user2 = User.objects.create_user(username='voong.hannah@gmail.com', password='password')
        Transaction.objects.create(user=user1, date=today, size=10, description='description', closing_balance=10)
        Transaction.objects.create(user=user2, date=today, size=100, description='description2', closing_balance=100)
        self.client.login(username='voong.david@gmail.com', password='password')
        response = self.client.get('/home')
        self.assertEqual(list(response.context['transactions']), list(Transaction.objects.filter(user=user1)))

class TestRegistration(TestCase):

    def test_url_resolution(self):
        resolver = resolve('/register')
        self.assertEqual(resolver.view_name, 'register')
    
    def test_register_new_user(self):
        self.client.post('/register', {'email': 'voong.david@gmail.com', 'password': 'password'})
        user = User.objects.get(username='voong.david@gmail.com')

class TestCreateTransaction(TestCase):

    def setUp(self):
        User.objects.create_user(username='voong.david@gmail.com', email='voong.david@gmail.com', password='password')
        self.client.login(username='voong.david@gmail.com', password='password')
    
    def test_url_resolution(self):
        resolver = resolve('/create-transaction')
        self.assertEqual(resolver.view_name, 'create_transaction')

    def test(self):
        self.client.post('/create-transaction', {'date': '2018-01-01', 'size': 1000, 'description': 'pay day'})
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 1)
        t = transactions[0]
        self.assertEqual(t.date, datetime.date(2018, 1, 1))
        self.assertEqual(t.size, 1000)
        self.assertEqual(t.description, 'pay day')
