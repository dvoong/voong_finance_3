import datetime
import pandas as pd
from functional_tests.TestCase import TestCase
from functional_tests.homepage.HomePage import HomePage
from functional_tests.welcome.WelcomePage import WelcomePage

class TestUpdatesClosingBalance(TestCase):

    def setUp(self):
        super().setUp()
        self.user = self.create_user('voong.david@gmail.com', 'password')

    def test(self):

        self.driver.get(self.live_server_url)
        welcome_page = WelcomePage(self.driver)
        welcome_page.login_user('voong.david@gmail.com', 'password')

        start = datetime.date(2018, 1, 1)
        end = datetime.date(2018, 1, 15)
        homepage = HomePage(self.driver, self.live_server_url, start, end)

        homepage.create_transaction(
            date=datetime.date(2018, 1, 1),
            size=1,
            description='a'
        )

        homepage = homepage.reload()
        homepage.create_transaction(
            date=datetime.date(2018, 1, 1),
            size=2,
            description='b',
            repeats='weekly',
            ends={'how': 'never_ends'}
        )

        balances = homepage.get_balances()
        transactions = homepage.get_transactions()

        dates = pd.date_range(datetime.date(2018, 1, 1), datetime.date(2018, 1, 15))
        values = [3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 7.0]
        balances_expected = pd.DataFrame({'date': dates, 'balance': values})
        balances_expected = balances_expected.set_index('date')

        self.assertTrue(balances.equals(balances_expected), (balances, balances_expected))

        values = [(t.date, t.size, t.description, t.balance) for t in transactions]
        transactions = pd.DataFrame(
            values,
            columns=['date', 'size', 'description', 'closing_balance']
        )
        
        transactions_expected = [
            (datetime.date(2018, 1, 1), 1.0, 'a', '£1.00'),
            (datetime.date(2018, 1, 1), 2.0, 'b', '£3.00'),
            (datetime.date(2018, 1, 8), 2.0, 'b', '£5.00'),
            (datetime.date(2018, 1, 15), 2.0, 'b', '£7.00')
        ]

        transactions_expected = pd.DataFrame(
            transactions_expected,
            columns=['date', 'size', 'description', 'closing_balance']
        )

        self.assertTrue(
            transactions.equals(transactions_expected),
            (transactions, transactions_expected)
        )
