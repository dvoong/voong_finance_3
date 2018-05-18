import datetime as dt
from functional_tests.TestCase import TestCase
from functional_tests.homepage.HomePage import HomePage

class TestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.create_user('voong.david@gmail.com', 'password')
        self.sign_in('voong.david@gmail.com', 'password')

class TestUpdateTransaction(TestCase):

    def test(self):

        url = '{}/home?start=2018-01-01&end=2018-01-15'.format(self.live_server_url)
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

        # change start date to a week earlier
        rt.start_date = dt.date(2017, 12, 25)
        rt.save()

        # payments will start a week earlier
        # balance will be modified to reflect this
        url = '{}/home?start=2017-12-25&end=2018-01-15'.format(self.live_server_url)
        self.driver.get(url)
        home_page = HomePage(self.driver)
        transactions = home_page.get_transactions()
        self.assertEqual(len(transactions), 4)
        self.assertEqual(transactions[0].date, dt.date(2017, 12, 25))
        self.assertEqual(transactions[0].balance, '£1.00')
        self.assertEqual(transactions[1].date, dt.date(2018, 1, 1))
        self.assertEqual(transactions[1].balance, '£2.00')

        # change start date to a week later

        # change size

        # change description

        # set an end criteria

        # test payments with a specified end point
        
        self.assertTrue(False, 'TODO')
        
