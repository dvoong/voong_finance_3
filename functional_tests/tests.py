import time
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

        self.balance_chart = driver.find_element_by_id('balance-chart')
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
        return self.element.find_element_by_css_selector('.transaction')

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
        f = homepage.transaction_form
        f.date_input.send_keys('01012018')
        f.transaction_size_input.send_keys('1000')
        f.description_input.send_keys('pay day')
        f.submit_button.click()

        homepage = HomePage(self.driver)
        t = homepage.transaction_list
        transactions = t.get_transactions()
        self.assertEqual(len(transactions), 1)
