import unittest
import datetime as dt
from functional_tests.TestCase import TestCase
from functional_tests.homepage.HomePage import HomePage

class TestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.create_user('voong.david@gmail.com', 'password')
        self.sign_in('voong.david@gmail.com', 'password')

def check_transactions(test_case, home_page, expected):

    transactions = home_page.get_transactions()
    test_case.assertEqual(len(expected), len(transactions))

    for t, exp in zip(transactions, expected):
        test_case.assertEqual(
            (t.date, t.size, t.description, t.balance),
            exp
        )

class TestUpdateTransaction(TestCase):

    def setUp(self):
        super().setUp()

        url = '{}/home?start=2018-01-01&end=2018-01-22'.format(self.live_server_url)
        self.driver.get(url)
        
        home_page = HomePage(self.driver)
        home_page.create_transaction(
            date=dt.date(2018, 1, 1),
            size=1,
            description='a',
            repeats='weekly',
            ends={'how': 'never_ends'})
                                     
        home_page.show_repeat_transactions_view()

        repeat_transactions = home_page.get_repeat_transactions()
        self.assertEqual(len(repeat_transactions), 1)

        rt = repeat_transactions[0]
        self.assertEqual(rt.start_date, dt.date(2018, 1, 1))
        self.assertEqual(rt.size, 1)
        self.assertEqual(rt.description, 'a')
        self.assertEqual(rt.frequency, 'weekly')
        self.assertEqual(rt.ends, 'never')

        self.repeat_transaction = rt
        self.home_page = home_page

    def check_transactions(self, expected):
        return check_transactions(self, self.home_page, expected)
        
    def test_make_transaction_earlier(self):

        # change start date to a week earlier
        rt = self.repeat_transaction
        rt.start_date = dt.date(2017, 12, 25)
        rt.save()

        home_page = self.home_page
        url = '{}/home?start=2017-12-25&end=2018-01-22'.format(self.live_server_url)
        self.driver.get(url)
        home_page.reload()
        
        expected = [
            (dt.date(2017, 12, 25), 1, 'a', '£1.00'),
            (dt.date(2018, 1, 1), 1, 'a', '£2.00'),
            (dt.date(2018, 1, 8), 1, 'a', '£3.00'),
            (dt.date(2018, 1, 15), 1, 'a', '£4.00'),
            (dt.date(2018, 1, 22), 1, 'a', '£5.00')
        ]

        self.check_transactions(expected)

    def test_make_transaction_later(self):

        # change start date to a week later
        rt = self.repeat_transaction
        rt.start_date = dt.date(2018, 1, 8)
        rt.save()

        self.home_page.reload()
        expected = [
            (dt.date(2018, 1, 8), 1, 'a', '£1.00'),
            (dt.date(2018, 1, 15), 1, 'a', '£2.00'),
            (dt.date(2018, 1, 22), 1, 'a', '£3.00'),
        ]
        self.check_transactions(expected)
        
    def test_change_size(self):

        # change size
        rt = self.repeat_transaction
        rt.size = 2
        rt.save()

        self.home_page.reload()

        expected = [
            (dt.date(2018, 1, 1), 2, 'a', '£2.00'),
            (dt.date(2018, 1, 8), 2, 'a', '£4.00'),
            (dt.date(2018, 1, 15), 2, 'a', '£6.00'),
            (dt.date(2018, 1, 22), 2, 'a', '£8.00')
        ]

        self.check_transactions(expected)

    def test_change_description(self):

        # change size
        rt = self.repeat_transaction
        rt.description = 'b'
        rt.save()

        self.home_page.reload()

        expected = [
            (dt.date(2018, 1, 1), 1, 'b', '£1.00'),
            (dt.date(2018, 1, 8), 1, 'b', '£2.00'),
            (dt.date(2018, 1, 15), 1, 'b', '£3.00'),
            (dt.date(2018, 1, 22), 1, 'b', '£4.00')
        ]
        
        self.check_transactions(expected)

    def test_change_end_criteria(self):

        # change date
        rt = self.repeat_transaction
        rt.ends = dt.date(2018, 1, 15)
        rt.save()

        self.home_page.reload()

        expected = [
            (dt.date(2018, 1, 1), 1, 'a', '£1.00'),
            (dt.date(2018, 1, 8), 1, 'a', '£2.00'),
            (dt.date(2018, 1, 15), 1, 'a', '£3.00'),
        ]

        self.check_transactions(expected)
        

class TestUpdateRepeatTransactionThousands(TestCase):

    def test(self):

        url = '{}/home?start=2018-01-01&end=2018-01-22'.format(self.live_server_url)
        self.driver.get(url)
        
        home_page = HomePage(self.driver)
        home_page.create_transaction(
            date=dt.date(2018, 1, 1),
            size=1000,
            description='a',
            repeats='weekly',
            ends={'how': 'ends_after_#_transactions', 'when': 2})
                                     
        home_page.show_repeat_transactions_view()

        repeat_transactions = home_page.get_repeat_transactions()
        self.assertEqual(len(repeat_transactions), 1)

        rt = repeat_transactions[0]
        self.assertEqual(rt.start_date, dt.date(2018, 1, 1))
        self.assertEqual(rt.size, 1000)
        self.assertEqual(rt.description, 'a')
        self.assertEqual(rt.frequency, 'weekly')
        self.assertEqual(rt.ends, dt.date(2018, 1, 8))

        # change date
        rt.ends = dt.date(2018, 1, 15)
        import time
        time.sleep(15)
        rt.save()

        home_page.reload()

        expected = [
            (dt.date(2018, 1, 1), 1000, 'a', '£1,000.00'),
            (dt.date(2018, 1, 8), 1000, 'a', '£2,000.00'),
            (dt.date(2018, 1, 15), 1000, 'a', '£3,000.00'),
        ]

        check_transactions(self, home_page, expected)

    
