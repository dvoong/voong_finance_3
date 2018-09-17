import datetime
from functional_tests.TestCase import TestCase
from functional_tests.homepage.HomePage import HomePage, BalanceChart
from functional_tests.welcome.WelcomePage import WelcomePage
from selenium.webdriver.support.ui import Select, WebDriverWait

strptime = datetime.datetime.strptime
        
class TestDateSelection(TestCase):

    def setUp(self):
        super().setUp()
        self.create_user(email="voong.david@gmail.com", password="password")

    def test(self):
        self.driver.get(self.live_server_url)
        welcome_page = WelcomePage(self.driver)
        welcome_page.login_user(email="voong.david@gmail.com", password="password")

        today = datetime.date.today()
        last_month = today - datetime.timedelta(days=41)

        homepage = HomePage(self.driver)
        homepage.create_transaction(date=last_month, size=100, description='a', update=True)

        homepage.create_transaction(date=today, size=-50, description='b', update=True)
        
        balance_chart = homepage.balance_chart

        self.assertEqual(balance_chart.bars[0].balance, 100)
        self.assertEqual(balance_chart.bars[len(balance_chart.bars) // 2].balance, 50)
        
        date_selector = homepage.date_selector
        self.assertEqual(date_selector.start, today - datetime.timedelta(days=41))
        self.assertEqual(date_selector.end, today + datetime.timedelta(days=42))

        date_selector.start = last_month
        date_selector.end = last_month + datetime.timedelta(days=7)
        date_selector.submit()

        homepage = HomePage(self.driver)
        balance_chart = homepage.balance_chart

        self.assertEqual(len(balance_chart.bars), 8)
        self.assertEqual(balance_chart.bars[0].balance, 100)
        self.assertEqual(balance_chart.bars[0].date, last_month)
        self.assertEqual(balance_chart.bars[7].balance, 100)
        self.assertEqual(balance_chart.bars[7].date, last_month + datetime.timedelta(days=7))

class TestDateRangeSelector(TestCase):

    def setUp(self):
        super().setUp()
        self.create_user(email="voong.david@gmail.com", password="password")

    def test(self):
        self.driver.get(self.live_server_url)
        welcome_page = WelcomePage(self.driver)
        welcome_page.login_user(email="voong.david@gmail.com", password="password")

        today = datetime.date.today()
        homepage = HomePage(self.driver)
        homepage.create_transaction(date=today, size=10, description='a', update=True)

        week_forward_button = self.driver.find_element_by_id('week-forward-button')
        week_backward_button = self.driver.find_element_by_id('week-backward-button')

        date_range = homepage.get_date_range()
        homepage.move_date_range_forward(days=7)
        WebDriverWait(self.driver, timeout=2).until(
            lambda b: homepage.get_date_range() == [today - datetime.timedelta(days=34),
                          today + datetime.timedelta(days=49)]
        )

        date_range = homepage.get_date_range()
        homepage.move_date_range_backward(days=7)
        WebDriverWait(self.driver, timeout=2).until(
            lambda b: homepage.get_date_range() == [date_range[0] - datetime.timedelta(days=7),
                          date_range[1] - datetime.timedelta(days=7)]
        )

        date_range = homepage.get_date_range()
        homepage.move_date_range_backward(days=7)
        WebDriverWait(self.driver, timeout=2).until(
            lambda b: homepage.get_date_range() == [
                date_range[0] - datetime.timedelta(days=7),
                date_range[1] - datetime.timedelta(days=7)
            ]
        )
