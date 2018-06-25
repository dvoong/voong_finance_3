import unittest
import datetime as dt
from functional_tests.TestCase import TestCase
from functional_tests.homepage.HomePage import HomePage

class TestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.create_user('voong.david@gmail.com', 'password')
        self.sign_in('voong.david@gmail.com', 'password')

class TestUpdateTransaction(TestCase):

    def test_make_transaction_earlier(self):

        url = '{}/home?start=2018-01-01&end=2018-01-15'.format(self.live_server_url)
        self.driver.get(url)
        
        home_page = HomePage(self.driver)
        home_page.create_transaction(
            date=dt.date(2018, 1, 1),
            size=1,
            description='a',
            repeats='weekly',
            ends={'how': 'never'})

        home_page.create_transaction(
            date=dt.date(2018, 1, 1),
            size = 2,
            description='b',
        )
                                     
        home_page.show_repeat_transactions_view()

        repeat_transactions = home_page.get_repeat_transactions()
        self.assertEqual(len(repeat_transactions), 1)

        rt = repeat_transactions[0]
        self.assertEqual(rt.start_date, dt.date(2018, 1, 1))
        self.assertEqual(rt.size, 1)
        self.assertEqual(rt.description, 'a')
        self.assertEqual(rt.frequency, 'weekly')
        self.assertEqual(rt.ends, 'never')

        # change start date to a week earlier
        rt.start_date = dt.date(2017, 12, 25)
        rt.save()

        # payments will start a week earlier
        # balance will be modified to reflect this
        url = '{}/home?start=2017-12-25&end=2018-01-15'.format(self.live_server_url)
        self.driver.get(url)
        home_page = HomePage(self.driver)
        transactions = home_page.get_transactions()
        self.assertEqual(len(transactions), 5)
        
        expected = [
            (dt.date(2017, 12, 25), 1, 'a', '£1.00'),
            (dt.date(2018, 1, 1), 1, 'a', '£2.00'),
            (dt.date(2018, 1, 1), 2, 'b', '£4.00'),
            (dt.date(2018, 1, 8), 1, 'a', '£5.00'),
            (dt.date(2018, 1, 15), 1, 'a', '£6.00')
        ]

        for t, exp in zip(transactions, expected):
            self.assertEqual(
                (t.date, t.size, t.description, t.balance),
                exp
            )

    def test_make_transaction_later(self):

        url = '{}/home?start=2018-01-01&end=2018-01-22'.format(self.live_server_url)
        self.driver.get(url)
        
        home_page = HomePage(self.driver)
        home_page.create_transaction(
            date=dt.date(2018, 1, 1),
            size=1,
            description='a',
            repeats='weekly',
            ends={'how': 'never'})
                                     
        home_page.show_repeat_transactions_view()

        repeat_transactions = home_page.get_repeat_transactions()
        self.assertEqual(len(repeat_transactions), 1)

        rt = repeat_transactions[0]
        self.assertEqual(rt.start_date, dt.date(2018, 1, 1))
        self.assertEqual(rt.size, 1)
        self.assertEqual(rt.description, 'a')
        self.assertEqual(rt.frequency, 'weekly')
        self.assertEqual(rt.ends, 'never')

        # change start date to a week later
        rt.start_date = dt.date(2018, 1, 8)
        rt.save()

        # change start date to a week later
        url = '{}/home?start=2018-01-01&end=2018-01-22'.format(self.live_server_url)
        self.driver.get(url)
        home_page = HomePage(self.driver)
        transactions = home_page.get_transactions()
        self.assertEqual(len(transactions), 3)
        self.assertEqual(transactions[0].date, dt.date(2018, 1, 8))
        self.assertEqual(transactions[0].balance, '£1.00')
        self.assertEqual(transactions[1].date, dt.date(2018, 1, 15))
        self.assertEqual(transactions[1].balance, '£2.00')
        self.assertEqual(transactions[2].date, dt.date(2018, 1, 22))
        self.assertEqual(transactions[2].balance, '£3.00')

    def test_change_size(self):

        url = '{}/home?start=2018-01-01&end=2018-01-22'.format(self.live_server_url)
        self.driver.get(url)
        
        home_page = HomePage(self.driver)
        home_page.create_transaction(
            date=dt.date(2018, 1, 1),
            size=1,
            description='a',
            repeats='weekly',
            ends={'how': 'never'})
                                     
        home_page.show_repeat_transactions_view()

        repeat_transactions = home_page.get_repeat_transactions()
        self.assertEqual(len(repeat_transactions), 1)

        rt = repeat_transactions[0]
        self.assertEqual(rt.start_date, dt.date(2018, 1, 1))
        self.assertEqual(rt.size, 1)
        self.assertEqual(rt.description, 'a')
        self.assertEqual(rt.frequency, 'weekly')
        self.assertEqual(rt.ends, 'never')

        # change size
        rt.size = 2
        rt.save()

        home_page.reload()

        transactions = home_page.get_transactions()
        self.assertEqual(len(transactions), 4)
        expected = [
            (dt.date(2018, 1, 1), 'a', 2, '£2.00'),
            (dt.date(2018, 1, 8), 'a', 2, '£4.00'),
            (dt.date(2018, 1, 15), 'a', 2, '£6.00'),
            (dt.date(2018, 1, 22), 'a', 2, '£8.00')
        ]
        for t, exp in zip(transactions, expected):
            self.assertEqual(
                (t.date, t.description, t.size, t.balance),
                exp
            )

    def test_change_description(self):
        pass
        # # set an end criteria

        # # test payments with a specified end point
        
        # self.assertTrue(False, 'TODO')
        
