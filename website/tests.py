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
        Transaction.objects.create(user=user1, date=today, size=10, description='description', closing_balance=10, index=0)
        Transaction.objects.create(user=user2, date=today, size=100, description='description2', closing_balance=100, index=0)
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
        self.user = User.objects.create_user(username='voong.david@gmail.com', email='voong.david@gmail.com', password='password')
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
        self.assertEqual(t.index, 0)

    def test_create_past_transaction(self):
        Transaction.objects.create(date=datetime.date(2018, 1, 2), size=100, description='dividends received', user=self.user, closing_balance=100, index=0)
        self.client.post('/create-transaction', {'date': '2018-01-01', 'size': 1000, 'description': 'pay day'})
        transactions = Transaction.objects.all().order_by('date')
        self.assertEqual(len(transactions), 2)

        t = transactions[0]
        self.assertEqual(t.date, datetime.date(2018, 1, 1))
        self.assertEqual(t.size, 1000)
        self.assertEqual(t.description, 'pay day')
        self.assertEqual(t.closing_balance, 1000)
        self.assertEqual(t.index, 0)

        t = transactions[1]
        self.assertEqual(t.date, datetime.date(2018, 1, 2))
        self.assertEqual(t.size, 100)
        self.assertEqual(t.description, 'dividends received')
        self.assertEqual(t.closing_balance, 1100)
        self.assertEqual(t.index, 0)

    def test_create_multiple_transactions_on_the_same_date(self):
        Transaction.objects.create(date=datetime.date(2018, 1, 2), size=100, description='dividends received', user=self.user, closing_balance=100, index=0)
        self.client.post('/create-transaction', {'date': '2018-01-02', 'size': 1000, 'description': 'pay day'})
        transactions = Transaction.objects.all().order_by('date', 'index')
        self.assertEqual(len(transactions), 2)

        t = transactions[0]
        self.assertEqual(t.date, datetime.date(2018, 1, 2))
        self.assertEqual(t.size, 100)
        self.assertEqual(t.description, 'dividends received')
        self.assertEqual(t.closing_balance, 100)
        self.assertEqual(t.index, 0)

        t = transactions[1]
        self.assertEqual(t.date, datetime.date(2018, 1, 2))
        self.assertEqual(t.size, 1000)
        self.assertEqual(t.description, 'pay day')
        self.assertEqual(t.closing_balance, 1100)
        self.assertEqual(t.index, 1)
                

class TestTransactionUpdate(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='voong.david@gmail.com', email='voong.david@gmail.com', password='password')
        self.client.login(username='voong.david@gmail.com', password='password')
    
    def test_url_resolution(self):
        resolver = resolve('/create-transaction')
        self.assertEqual(resolver.view_name, 'create_transaction')

    def test(self):
        self.client.post('/create-transaction', {'date': '2018-01-01', 'size': '1000.00', 'description': 'pay day'})
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 1)
        t = transactions[0]
        transaction_id = t.id
        self.client.post('/update-transaction', {'date': '2018-01-02', 'size': '1000.00', 'description': 'pay day', 'id': str(transaction_id)})
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 1)
        t = transactions[0]
        self.assertEqual(t.date, datetime.date(2018, 1, 2))
        self.assertEqual(t.size, 1000)
        self.assertEqual(t.description, 'pay day')
        self.assertEqual(t.id, transaction_id)

    def test_recalculates_closing_balance(self):
        a = Transaction.objects.create(user=self.user, date='2018-01-01', size=1, description='a', id=1, closing_balance=1, index=0)
        b = Transaction.objects.create(user=self.user, date='2018-01-02', size=10, description='b', id=2, closing_balance=11, index=1)
        c = Transaction.objects.create(user=self.user, date='2018-01-03', size=100, description='c', id=3, closing_balance=111, index=2)
        self.client.post('/update-transaction', {'date': '2017-12-31', 'size': '10.00', 'description': 'b', 'id': str(2)})
        a = Transaction.objects.get(pk=1)
        b = Transaction.objects.get(pk=2)
        c = Transaction.objects.get(pk=3)
        self.assertEqual(b.date, datetime.date(2017, 12, 31))
        self.assertEqual(b.closing_balance, 10)
        self.assertEqual(a.closing_balance, 11)
        self.assertEqual(c.closing_balance, 111)

    def test_recalculates_closing_balance_date_and_size_change(self):
        a = Transaction.objects.create(user=self.user, date='2018-01-01', size=1, description='a', id=1, closing_balance=1, index=0)
        b = Transaction.objects.create(user=self.user, date='2018-01-02', size=10, description='b', id=2, closing_balance=11, index=1)
        c = Transaction.objects.create(user=self.user, date='2018-01-03', size=100, description='c', id=3, closing_balance=111, index=2)
        self.client.post('/update-transaction', {'date': '2017-12-31', 'size': '20.00', 'description': 'b', 'id': str(2)})
        a = Transaction.objects.get(pk=1)
        b = Transaction.objects.get(pk=2)
        c = Transaction.objects.get(pk=3)
        self.assertEqual(b.date, datetime.date(2017, 12, 31))
        self.assertEqual(b.size, 20)
        self.assertEqual(b.closing_balance, 20)
        self.assertEqual(a.closing_balance, 21)
        self.assertEqual(c.closing_balance, 121)

    def test_move_transaction_to_a_date_with_another_transaction(self):
        a = Transaction.objects.create(user=self.user, date='2018-01-01', size=1, description='a', id=1, closing_balance=1, index=0)
        b = Transaction.objects.create(user=self.user, date='2018-01-02', size=10, description='b', id=2, closing_balance=11, index=0)
        self.client.post('/update-transaction', {'date': '2018-01-01', 'size': '10.00', 'description': 'b', 'id': str(2)})
        a = Transaction.objects.get(pk=1)
        self.assertEqual(a.index, 0)
        b = Transaction.objects.get(pk=2)
        self.assertEqual(b.date, datetime.date(2018, 1, 1))
        self.assertEqual(b.size, 10)
        self.assertEqual(b.closing_balance, 11)
        self.assertEqual(b.index, 1)
        
