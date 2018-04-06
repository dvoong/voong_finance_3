import datetime as dt
from functional_tests.TestCase import TestCase
from functional_tests.HomePage import HomePage
from functional_tests.WelcomePage import WelcomePage

class TestRepeatTransactionTab(TestCase):

    def setUp(self):
        super().setUp()
        self.create_user(email='voong.david@gmail.com', password='password')
        self.driver.get(self.live_server_url)
        welcome_page = WelcomePage(self.driver)
        welcome_page.login_user(email='voong.david@gmail.com', password='password')

    def test(self):

        home_page = HomePage(self.driver)
        home_page.create_transaction(date=dt.date(2018, 1, 1),
                                     size=10,
                                     description='a',
                                     repeats='weekly',
                                     ends={'how': 'never'})

        home_page.show_repeat_transactions_view()
        home_page.repeat_transactions_list.assert_in(
            date=dt.date(2018, 1, 1),
            size=10,
            description='a',
            repeats='weekly',
            ends='never')
        
