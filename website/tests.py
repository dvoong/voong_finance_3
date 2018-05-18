import datetime
import pandas as pd
from unittest.mock import patch
from django.test import TestCase
from django.urls import resolve
from django.contrib.auth.models import User
from django.contrib import auth
from website.models import Transaction, RepeatTransaction

import datetime as dt

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
        User.objects.create_user(username='voong.david@gmail.com',
                                 email='voong.david@gmail.com',
                                 password='password')
    
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
        user = User.objects.create_user(username='voong.david@gmail.com',
                                        email='voong.david@gmail.com',
                                        password='password')
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
        user = User.objects.create_user(username='voong.david@gmail.com',
                                        email='voong.david@gmail.com',
                                        password='password')
        self.client.login(username='voong.david@gmail.com', password='password')
        response = self.client.get('/home')
        self.assertTemplateUsed(response, 'website/home.html')

    def test_populates_transactions_list(self):
        today = datetime.date.today()
        user1 = User.objects.create_user(username='voong.david@gmail.com', password='password')
        user2 = User.objects.create_user(username='voong.hannah@gmail.com', password='password')
        Transaction.objects.create(user=user1,
                                   date=today,
                                   size=10,
                                   description='description',
                                   closing_balance=10,
                                   index=0)
        Transaction.objects.create(user=user2,
                                   date=today,
                                   size=100,
                                   description='description2',
                                   closing_balance=100,
                                   index=0)
        self.client.login(username='voong.david@gmail.com', password='password')
        response = self.client.get('/home')

        expected = Transaction.objects.filter(user=user1).values()
        expected = pd.DataFrame(list(expected))
        expected['date'] = pd.to_datetime(expected['date'])
        expected['date'] = expected['date'].dt.strftime('%Y-%m-%d')
        expected = expected.to_json(orient='records')
        actual = response.context['transactions']
        
        self.assertEqual(actual, expected)

class TestRegistration(TestCase):

    def test_url_resolution(self):
        resolver = resolve('/register')
        self.assertEqual(resolver.view_name, 'register')
    
    def test_register_new_user(self):
        self.client.post('/register', {'email': 'voong.david@gmail.com', 'password': 'password'})
        user = User.objects.get(username='voong.david@gmail.com')

class TestCreateTransaction(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='voong.david@gmail.com',
                                             email='voong.david@gmail.com', password='password')
        self.client.login(username='voong.david@gmail.com',
                          password='password')
    
    def test_url_resolution(self):
        resolver = resolve('/create-transaction')
        self.assertEqual(resolver.view_name, 'create_transaction')

    def test(self):
        self.client.post('/create-transaction',
                         {'date': '2018-01-01', 'size': 1000, 'description': 'pay day'})
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 1)
        t = transactions[0]
        self.assertEqual(t.date, datetime.date(2018, 1, 1))
        self.assertEqual(t.size, 1000)
        self.assertEqual(t.description, 'pay day')
        self.assertEqual(t.index, 0)

    def test_create_past_transaction(self):
        Transaction.objects.create(date=datetime.date(2018, 1, 2),
                                   size=100,
                                   description='dividends received',
                                   user=self.user,
                                   closing_balance=100,
                                   index=0)
        self.client.post('/create-transaction',
                         {'date': '2018-01-01', 'size': 1000, 'description': 'pay day'})
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
        Transaction.objects.create(date=datetime.date(2018, 1, 2),
                                   size=100,
                                   description='dividends received',
                                   user=self.user,
                                   closing_balance=100,
                                   index=0)
        self.client.post('/create-transaction',
                         {'date': '2018-01-02', 'size': 1000, 'description': 'pay day'})
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

    def test_create_repeat_transaction_ends_on_n_occurrences(self):
        
        self.client.post('/create-transaction',
                         {
                             'date': '2018-01-01',
                             'size': 1,
                             'description': 'a',
                             'frequency': 'weekly',
                             'repeat_status': 'repeats',
                             'end_condition': 'n_occurrences',
                             'n_occurrences': 2
                         }
        )

        self.client.get('/home', {'start': '2018-01-01', 'end': '2018-01-15'})

        repeat_transactions = RepeatTransaction.objects.all()
        self.assertEqual(len(repeat_transactions), 1)

        r = repeat_transactions[0]
        self.assertEqual(r.end_date, datetime.date(2018, 1, 8))
        
        transactions = Transaction.objects.all().order_by('date', 'index')
        self.assertEqual(len(transactions), 2)
        
        t = transactions[0]
        self.assertEqual(t.date, datetime.date(2018, 1, 1))
        self.assertEqual(t.size, 1)
        self.assertEqual(t.description, 'a')
        self.assertEqual(t.closing_balance, 1)
        self.assertEqual(t.index, 0)

        t = transactions[1]
        self.assertEqual(t.date, datetime.date(2018, 1, 8))
        self.assertEqual(t.size, 1)
        self.assertEqual(t.description, 'a')
        self.assertEqual(t.closing_balance, 2)
        self.assertEqual(t.index, 0)

class TestTransactionUpdate(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='voong.david@gmail.com',
                                             email='voong.david@gmail.com',
                                             password='password')
        self.client.login(username='voong.david@gmail.com', password='password')
    
    def test_url_resolution(self):
        resolver = resolve('/create-transaction')
        self.assertEqual(resolver.view_name, 'create_transaction')

    def test(self):
        self.client.post('/create-transaction',
                         {'date': '2018-01-01', 'size': '1000.00', 'description': 'pay day'})
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 1)
        t = transactions[0]
        transaction_id = t.id
        self.client.post('/modify-transaction',
                         {
                             'date': '2018-01-02',
                             'size': '1000.00',
                             'description': 'pay day',
                             'id': str(transaction_id),
                             'action':'update'
                         })
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 1)
        t = transactions[0]
        self.assertEqual(t.date, datetime.date(2018, 1, 2))
        self.assertEqual(t.size, 1000)
        self.assertEqual(t.description, 'pay day')
        self.assertEqual(t.id, transaction_id)

    def test_recalculates_closing_balance(self):
        a = Transaction.objects.create(user=self.user,
                                       date='2018-01-01',
                                       size=1, description='a',
                                       id=1,
                                       closing_balance=1,
                                       index=0)
        b = Transaction.objects.create(user=self.user,
                                       date='2018-01-02',
                                       size=10,
                                       description='b',
                                       id=2,
                                       closing_balance=11,
                                       index=1)
        c = Transaction.objects.create(user=self.user,
                                       date='2018-01-03',
                                       size=100,
                                       description='c',
                                       id=3,
                                       closing_balance=111,
                                       index=2)
        self.client.post('/modify-transaction',
                         {'date': '2017-12-31',
                          'size': '10.00',
                          'description': 'b',
                          'id': str(2),
                          'action': 'update'})
        a = Transaction.objects.get(pk=1)
        b = Transaction.objects.get(pk=2)
        c = Transaction.objects.get(pk=3)
        self.assertEqual(b.date, datetime.date(2017, 12, 31))
        self.assertEqual(b.closing_balance, 10)
        self.assertEqual(a.closing_balance, 11)
        self.assertEqual(c.closing_balance, 111)

    def test_recalculates_closing_balance_date_and_size_change(self):
        a = Transaction.objects.create(user=self.user,
                                       date='2018-01-01',
                                       size=1,
                                       description='a',
                                       id=1,
                                       closing_balance=1,
                                       index=0)
        b = Transaction.objects.create(user=self.user,
                                       date='2018-01-02',
                                       size=10,
                                       description='b',
                                       id=2,
                                       closing_balance=11,
                                       index=1)
        c = Transaction.objects.create(user=self.user,
                                       date='2018-01-03',
                                       size=100,
                                       description='c',
                                       id=3,
                                       closing_balance=111,
                                       index=2)
        self.client.post('/modify-transaction',
                         {'date': '2017-12-31',
                          'size': '20.00',
                          'description': 'b',
                          'id': str(2),
                          'action': 'update'})
        a = Transaction.objects.get(pk=1)
        b = Transaction.objects.get(pk=2)
        c = Transaction.objects.get(pk=3)
        self.assertEqual(b.date, datetime.date(2017, 12, 31))
        self.assertEqual(b.size, 20)
        self.assertEqual(b.closing_balance, 20)
        self.assertEqual(a.closing_balance, 21)
        self.assertEqual(c.closing_balance, 121)

    def test_move_transaction_to_a_date_with_another_transaction(self):
        a = Transaction.objects.create(user=self.user,
                                       date='2018-01-01',
                                       size=1,
                                       description='a',
                                       id=1,
                                       closing_balance=1,
                                       index=0)
        b = Transaction.objects.create(user=self.user,
                                       date='2018-01-02',
                                       size=10,
                                       description='b',
                                       id=2,
                                       closing_balance=11,
                                       index=0)
        self.client.post('/modify-transaction',
                         {'date': '2018-01-01',
                          'size': '10.00',
                          'description': 'b',
                          'id': str(2),
                          'action': 'update'})
        a = Transaction.objects.get(pk=1)
        self.assertEqual(a.index, 0)
        b = Transaction.objects.get(pk=2)
        self.assertEqual(b.date, datetime.date(2018, 1, 1))
        self.assertEqual(b.size, 10)
        self.assertEqual(b.closing_balance, 11)
        self.assertEqual(b.index, 1)
        
class TestSignOut(TestCase):

    def test_url_resolution(self):
        resolver = resolve('/sign-out')
        self.assertEqual(resolver.view_name, 'sign_out')

    def test(self):

        user = User.objects.create_user(username='voong.david@gmail.com',
                                        email='voong.david@gmail.com',
                                        password='password')
        self.client.login(username='voong.david@gmail.com', password='password')
        response = self.client.get('/sign-out')
        user = auth.get_user(self.client)
        self.assertEqual(user.is_authenticated, False)
        self.assertRedirects(response, '/welcome')

class TestGetBalances(TestCase):

    def test_url_resolution(self):
        resolver = resolve('/get-balances')
        self.assertEqual(resolver.view_name, 'get_balances')

    def test(self):
        username1 = 'voong.david@gmail.com'
        password1 = 'password'
        username2 = 'voong.hannah@gmail.com'
        password2 = 'hannah'
        user1 = User.objects.create_user(username=username1, email=username1, password=password1)
        user2 = User.objects.create_user(username=username2, email=username2, password=password2)

        transactions = [
            (datetime.date(2018, 1, 1), 10, 'a', user1, 10, 0),
            (datetime.date(2018, 1, 2), 5, 'b', user1, 15, 0),
            (datetime.date(2018, 1, 1), 20, 'c', user2, 20, 0),
        ]

        for t in transactions:
            Transaction.objects.create(date=t[0],
                                       size=t[1],
                                       description=t[2],
                                       user=t[3],
                                       closing_balance=t[4],
                                       index=t[5])
        
        self.client.login(username='voong.david@gmail.com', password='password')
        response = self.client.get('/get-balances', {'start': '2018-01-01', 'end': '2018-01-03'})
        expected = {
            'data': {
                'balances': [
                    {'date': '2018-01-01', 'balance': 10.0},
                    {'date': '2018-01-02', 'balance': 15.0},
                    {'date': '2018-01-03', 'balance': 15.0}
                ],
                'transactions': [
                    {
                        'closing_balance': 10.0,
                        'date': '2018-01-01',
                        'description': 'a',
                        'id': 1,
                        'index': 0,
                        'size': 10.0,
                        'user_id': 1,
                        'repeat_transaction_id': None
                    },
                    {
                        'closing_balance': 15.0,
                        'date': '2018-01-02',
                        'description': 'b',
                        'id': 2,
                        'index': 0,
                        'size': 5.0,
                        'user_id': 1,
                        'repeat_transaction_id': None
                    }
                ]
            }
        }

        actual = response.json()
        self.assertEqual(expected, actual)

    def test_repeating_transactions(self):
        user = User.objects.create_user(username="voong.david@gmail.com",
                                        email="voong.david@gmail.com",
                                        password="password")

        transaction = Transaction.objects.create(date=datetime.date(2018, 1, 1),
                                                 size=10,
                                                 description='a',
                                                 user=user,
                                                 closing_balance=10,
                                                 index=0)

        rt = RepeatTransaction.objects.create(start_date=datetime.date(2018, 1, 2),
                                              size=20,
                                              description='c',
                                              user=user,
                                              frequency='weekly',
                                              index=0)
        
        self.client.login(username='voong.david@gmail.com', password='password')
        response = self.client.get('/get-balances', {'start': '2018-01-01', 'end': '2018-01-09'})

        expected = {
            'data':
            {
                'balances':
                [
                    {'date': '2018-01-01', 'balance': 10.0},
                    {'date': '2018-01-02', 'balance': 30.0},
                    {'date': '2018-01-03', 'balance': 30.0},
                    {'date': '2018-01-04', 'balance': 30.0},
                    {'date': '2018-01-05', 'balance': 30.0},
                    {'date': '2018-01-06', 'balance': 30.0},
                    {'date': '2018-01-07', 'balance': 30.0},
                    {'date': '2018-01-08', 'balance': 30.0},
                    {'date': '2018-01-09', 'balance': 50.0}
                ],
                'transactions':
                [
                    {'closing_balance': 10.0,
                     'date': '2018-01-01',
                     'description': 'a',
                     'id': 1,
                     'index': 0,
                     'repeat_transaction_id': None,
                     'size': 10.0,
                     'user_id': 1
                    },
                    {
                        'closing_balance': 30.0,
                        'date': '2018-01-02',
                        'description': 'c',
                        'id': 2,
                        'index': 0,
                        'repeat_transaction_id': 1.0,
                        'size': 20.0, 'user_id': 1
                    },
                    {
                        'closing_balance': 50.0,
                        'date': '2018-01-09',
                        'description': 'c',
                        'id': 3,
                        'index': 0,
                        'repeat_transaction_id': 1.0,
                        'size': 20.0,
                        'user_id': 1
                    }
                ]
            }
        }

        actual = response.json()
        self.assertEqual(expected, actual)
            
class TestGetRepeatTransactionDeletionPrompt(TestCase):


    def test_url_resolution(self):
        resolver = resolve('/html-snippets/repeat-transaction-deletion-prompt')
        self.assertEqual(resolver.view_name, 'get_repeat_transaction_deletion_prompt')

    def test(self):
        response = self.client.get('/html-snippets/repeat-transaction-deletion-prompt')

class TestUpdateRepeatTransaction(TestCase):

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(username='voong.david@gmail.com',
                                             email='voong.david@gmail.com',
                                             password='password')
        self.client.login(username='voong.david@gmail.com', password='password')
        rt = RepeatTransaction.objects.create(
            start_date=dt.date(2018, 1, 1),
            size=1,
            description='a',
            user=self.user,
            index=0,
            frequency='weekly',
            id=0
        )

        for t in rt.generate_next_transaction(end=dt.date(2018, 1, 22)):
            t.save()

    def test_url_resolution(self):
        resolver = resolve('/update-repeat-transaction')
        self.assertEqual(resolver.view_name, 'update_repeat_transaction')

    def test(self):
        data = {
            'start': '2018-01-01',
            'end': '2018-01-08',
            'start_date': '2017-12-25',
            'id': 0
        }
        response = self.client.post('/update-repeat-transaction', data)
        self.assertRedirects(response, '/home?start=2018-01-01&end=2018-01-08')
        rt = RepeatTransaction.objects.get(id=0)
        self.assertEqual(rt.start_date, dt.date(2017, 12, 25))
        self.assertEqual(rt.size, 1)
        self.assertEqual(rt.description, 'a')

        # creates new transactions
        ts = Transaction.objects.filter(repeat_transaction=rt).order_by('date')
        self.assertEqual(len(ts), 5)
        self.assertEqual(ts[0].date, dt.date(2017, 12, 25))
        self.assertEqual(ts[0].closing_balance, 1)
        self.assertEqual(ts[1].date, dt.date(2018, 1, 1))
        self.assertEqual(ts[1].closing_balance, 2)
        self.assertEqual(ts[2].date, dt.date(2018, 1, 8))
        self.assertEqual(ts[2].closing_balance, 3)
        self.assertEqual(ts[3].date, dt.date(2018, 1, 15))
        self.assertEqual(ts[3].closing_balance, 4)
