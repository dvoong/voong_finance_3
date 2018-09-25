import datetime
import pandas as pd
from functional_tests.TestCase import TestCase
from functional_tests.homepage.RepeatTransaction import RepeatTransaction
from functional_tests.homepage.HomePage import HomePage
from functional_tests.welcome.WelcomePage import WelcomePage

class TestFornightlyRepeatTransaction(TestCase):

    def setUp(self):
        super().setUp()
        self.user = self.create_user('voong.david@gmail.com', 'password')

    def test(self):

        self.driver.get(self.live_server_url)
        welcome_page = WelcomePage(self.driver)
        welcome_page.login_user('voong.david@gmail.com', 'password')

        start=datetime.date(2018, 1, 1)
        end=datetime.date(2018, 1, 15)
        url = '{}/home?start={}&end={}'.format(self.live_server_url, start, end)
        self.driver.get(url)
        homepage = HomePage(self.driver)

        homepage.create_transaction(
            description='a',
            ends={'how': 'never_ends'},
            size=10,
            date=datetime.date(2018, 1, 1),
            steps=2,
            repeats='weekly',
        )
        
        homepage.reload()

        df_balances = homepage.get_balances()
        transactions = homepage.get_transactions()

        dates = pd.date_range(datetime.date(2018, 1, 1), datetime.date(2018, 1, 15))
        values = [10.0 for i in range(14)] + [20.0]
        df_expected = pd.DataFrame({'balance': values, 'date': dates})
        df_expected = df_expected.set_index('date')
        df_expected.index = pd.to_datetime(df_expected.index)

        self.assertTrue(df_balances.equals(df_expected), (df_balances, df_expected))

        
        
        
