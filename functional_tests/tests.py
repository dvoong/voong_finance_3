import time, datetime
from selenium.webdriver import Chrome
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User

class RegistrationForm:
    
    def __init__(self, driver):
        
        self.form = driver.find_element_by_id('registration-form')
        self.email_input = self.form.find_element_by_id('email-input')
        self.password_input = self.form.find_element_by_id('password-input')
        self.password_check_input = self.form.find_element_by_id('password-check-input')
        self.submit_button = self.form.find_element_by_id('submit-button')

class LoginForm:
    
    def __init__(self, driver):
        
        self.element = driver.find_element_by_id('login-form')
        self.email_input = self.element.find_element_by_id('email-input')
        self.password_input = self.element.find_element_by_id('password-input')
        self.submit_button = self.element.find_element_by_id('submit-button')

class HomePage:

    def __init__(self, driver):

        self.balance_chart = BalanceChart(driver)
        self.transaction_form = TransactionForm(driver)
        self.menu = Menu(driver)
        self.transaction_list = TransactionList(driver)

class TransactionForm:

    def __init__(self, driver):
        
        self.element = driver.find_element_by_id('transaction-form')
        self.date_input = self.element.find_element_by_id('date-input')
        self.transaction_size_input = self.element.find_element_by_id('transaction-size-input')
        self.description_input = self.element.find_element_by_id('description-input')
        self.submit_button = self.element.find_element_by_id('submit-button')

class Menu:

    def __init__(self, driver):
        self.element = driver.find_element_by_id('menu')

class TransactionList:

    def __init__(self, driver):

        self.element = driver.find_element_by_id('transaction-list')

    def get_transactions(self):
        return self.element.find_elements_by_css_selector('.transaction')

class BalanceChart:

    def __init__(self, driver):
        self.element = driver.find_element_by_id('balance-chart')
        self.canvas = self.element.find_element_by_id('canvas')
        self.x_axis = self.canvas.find_element_by_id('x-axis')
        self.y_axis = self.canvas.find_element_by_id('y-axis')
        self.plot_area = self.canvas.find_element_by_id('plot-area')

class TestRegistration(StaticLiveServerTestCase):

    def setUp(self):
        self.driver = Chrome()

    def test(self):
        self.driver.get(self.live_server_url)
        self.assertEqual(self.driver.current_url, self.live_server_url + '/welcome')
        self.assertEqual(self.driver.title, 'Welcome')

        registration_form = RegistrationForm(self.driver)
        login_form = LoginForm(self.driver)

        registration_form.email_input.send_keys('voong.david@gmail.com')
        registration_form.password_input.send_keys('password')
        registration_form.password_check_input.send_keys('password')

        registration_form.submit_button.click()

        homepage = HomePage(self.driver)

class TestLogin(StaticLiveServerTestCase):

    def setUp(self):
        self.driver = Chrome()
        User.objects.create_user(username='voong.david@gmail.com', email='voong.david@gmail.com', password='password')
        self.login()

    def login(self):
        self.driver.get(self.live_server_url)
        login_form = LoginForm(self.driver)
        login_form.email_input.send_keys('voong.david@gmail.com')
        login_form.password_input.send_keys('password')
        login_form.submit_button.click()

    def test(self):
        homepage = HomePage(self.driver)

class TestTransactionCreation(TestLogin):

    def test(self):
        homepage = HomePage(self.driver)
        today = datetime.date.today()

        f = homepage.transaction_form
        f.date_input.send_keys('{:02d}{:02d}{}'.format(today.day, today.month, today.year))
        f.transaction_size_input.send_keys('1000')
        f.description_input.send_keys('pay day')
        f.submit_button.click()

        homepage = HomePage(self.driver)
        transaction_list = homepage.transaction_list
        transactions = transaction_list.get_transactions()
        self.assertEqual(len(transactions), 1)
        
        t = transactions[0]
        cols = t.find_elements_by_css_selector('td')
        self.assertEqual(cols[0].text, today.isoformat())
        self.assertEqual(cols[1].text, '£1,000.00')
        self.assertEqual(cols[2].text, 'pay day')
        self.assertEqual(cols[3].text, '£1,000.00')

        balance_chart = homepage.balance_chart
        bars = balance_chart.plot_area.find_elements_by_css_selector('.bar')
        self.assertEqual(len(bars), 29)
        
        bar_today = bars[14]
        self.assertEqual(bar_today.get_attribute('date'), today.isoformat())
        self.assertEqual(bars[0].get_attribute('date'), (today - datetime.timedelta(days=14)).isoformat())
        self.assertEqual(bars[-1].get_attribute('date'), (today + datetime.timedelta(days=14)).isoformat())
        
        self.assertEqual(float(bar_today.get_attribute('balance')), 1000)
        self.assertEqual(float(bars[0].get_attribute('balance')), 0)
        self.assertEqual(float(bars[-1].get_attribute('balance')), 1000)
