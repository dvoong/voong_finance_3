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
        self.date_selector = DateSelector(driver.find_element_by_id('date-selector'))

class TransactionForm:

    def __init__(self, driver):
        
        self.element = driver.find_element_by_id('transaction-form')
        self.date_input = self.element.find_element_by_id('date-input')
        self.transaction_size_input = self.element.find_element_by_id('transaction-size-input')
        self.description_input = self.element.find_element_by_id('description-input')
        self.submit_button = self.element.find_element_by_id('submit-button')

    def create_transaction(self, date, size, description):
        self.date_input.send_keys('{:02d}{:02d}{}'.format(date.day, date.month, date.year))
        self.transaction_size_input.send_keys(size)
        self.description_input.send_keys(description)
        self.submit_button.click()

class Menu:

    def __init__(self, driver):
        self.element = driver.find_element_by_id('menu')

class TransactionList:

    def __init__(self, driver):

        self.element = driver.find_element_by_id('transaction-list')
        self.date_header = self.element.find_element_by_id('date-header')
        self.transaction_size_header = self.element.find_element_by_id('transaction-size-header')
        self.description_header = self.element.find_element_by_id('description-header')
        self.closing_balance_header = self.element.find_element_by_id('closing-balance-header')

    def get_transactions(self):
        transactions = []
        for e in self.element.find_elements_by_css_selector('.transaction'):
            transactions.append(Transaction(e))
        return transactions

class BalanceChart:

    def __init__(self, driver):
        self.element = driver.find_element_by_id('balance-chart')
        self.canvas = self.element.find_element_by_id('canvas')
        self.x_axis = self.canvas.find_element_by_id('x-axis')
        self.y_axis = self.canvas.find_element_by_id('y-axis')
        self.plot_area = self.canvas.find_element_by_id('plot-area')
        self.bars = [BalanceBar(element) for element in self.plot_area.find_elements_by_css_selector('.bar')]
        self.y_ticks = self.y_axis.text.split('\n')
        self.x_ticks = self.x_axis.text.split('\n')

class BalanceBar:

    def __init__(self, element):
        self.element = element
        self.balance = float(self.element.get_attribute('balance'))
        self.date = datetime.datetime.strptime(self.element.get_attribute('date'), '%Y-%m-%d').date()

class Transaction:

    def __init__(self, element):
        self.element = element
        self.date_input = self.element.find_element_by_css_selector('.date-input')
        self.size_input = self.element.find_element_by_css_selector('.transaction-size-input')
        self.description_input = self.element.find_element_by_css_selector('.description-input')
        self.balance_element = self.element.find_element_by_css_selector('.transaction-balance')
        self.id = self.element.find_element_by_css_selector('.id')
        self.save_button = self.element.find_element_by_css_selector('.save-transaction-button')
        self.delete_button = self.element.find_element_by_css_selector('.delete-transaction-button')
        
    @property
    def date(self):
        return datetime.datetime.strptime(self.date_input.get_attribute('value'), '%Y-%m-%d').date()

    @date.setter
    def date(self, date):
        keys = '{:02d}{:02d}{}'.format(date.day, date.month, date.year)        
        self.date_input.send_keys(keys)

    @property
    def size(self):
        return float(self.size_input.get_attribute('value'))

    @size.setter
    def size(self, size):
        self.size_input.clear()
        self.size_input.send_keys(size)

    @property
    def description(self):
        return self.description_input.get_attribute('value')

    @description.setter
    def description(self, description):
        self.description_input.clear()
        self.description_input.send_keys(description)

    @property
    def balance(self):
        return self.balance_element.text

    def save(self):
        self.save_button.click()

    def delete(self):
        self.delete_button.click()


class DateSelector:

    def __init__(self, element):
        self.element = element
        self.start_input = self.element.find_element_by_id('start-input')
        self.end_input = self.element.find_element_by_id('end-input')
        self.submit_button = self.element.find_element_by_css_selector('input[type="submit"]')

    @property
    def start(self):
        return datetime.datetime.strptime(self.start_input.get_attribute('value'), '%Y-%m-%d').date()

    @start.setter
    def start(self, date):
        keys = '{:02d}{:02d}{}'.format(date.day, date.month, date.year)        
        self.start_input.send_keys(keys)

    @property
    def end(self):
        return datetime.datetime.strptime(self.end_input.get_attribute('value'), '%Y-%m-%d').date()

    @end.setter
    def end(self, date):
        keys = '{:02d}{:02d}{}'.format(date.day, date.month, date.year)        
        self.end_input.send_keys(keys)

    def submit(self):
        self.submit_button.click()
        
        
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

class TransactionalTest(TestLogin):

    def create_transaction(self, date, size, description):
        homepage = HomePage(self.driver)        
        f = homepage.transaction_form
        f.create_transaction(date, size, description)

    def get_transactions(self):
        homepage = HomePage(self.driver)
        transaction_list = homepage.transaction_list
        transactions = transaction_list.get_transactions()
        return transactions
        
class TestTransactionCreation(TransactionalTest):

    def test(self):
        homepage = HomePage(self.driver)
        today = datetime.date.today()

        self.create_transaction(today, 1000, 'pay day')

        transactions = self.get_transactions()
        self.assertEqual(len(transactions), 1)
        
        t = transactions[0]
        self.assertEqual(t.date, today)
        self.assertEqual(t.size, 1000)
        self.assertEqual(t.description, 'pay day')
        self.assertEqual(t.balance, '£1,000.00')

        homepage = HomePage(self.driver)
        balance_chart = homepage.balance_chart
        bars = balance_chart.bars
        self.assertEqual(len(bars), 29)
        
        bar_today = bars[14]
        self.assertEqual(bar_today.date, today)
        self.assertEqual(bars[0].date, today - datetime.timedelta(days=14))
        self.assertEqual(bars[-1].date, today + datetime.timedelta(days=14))
        
        self.assertEqual(bar_today.balance, 1000)
        self.assertEqual(bars[0].balance, 0)
        self.assertEqual(bars[-1].balance, 1000)

        y_ticks = balance_chart.y_ticks
        for tick in y_ticks:
            number_int = int(tick.replace('£', '').replace(',', ''))
            number_float = float(tick.replace('£', '').replace(',', ''))
            self.assertTrue(tick.startswith('£'))
            self.assertEqual(number_int, number_float) # int numbers only
        
        ## creates another transaction before the first transaction - check balances calculted properly

        yesterday = today - datetime.timedelta(days=1)
        self.create_transaction(yesterday, 500, 'dividends received')

        transactions = self.get_transactions()
        self.assertEqual(len(transactions), 2)

        t = transactions[0]
        self.assertEqual(t.date, yesterday)
        self.assertEqual(t.size, 500)
        self.assertEqual(t.description, 'dividends received')
        self.assertEqual(t.balance, '£500.00')
        
        t = transactions[1]
        self.assertEqual(t.date, today)
        self.assertEqual(t.size, 1000)
        self.assertEqual(t.description, 'pay day')
        self.assertEqual(t.balance, '£1,500.00')
        
        # test modifying existing transactions
        t = transactions[1]
        tomorrow = today + datetime.timedelta(days=1)
        t.date = tomorrow
        t.save()

        transactions = self.get_transactions()
        self.assertEqual(len(transactions), 2)
        
        t = transactions[1]
        self.assertEqual(t.date, tomorrow)
        self.assertEqual(t.size, 1000)
        self.assertEqual(t.description, 'pay day')
        self.assertEqual(t.balance, '£1,500.00')
        
        # add test for when transaction gets updated to before a previous transaction, will need to recalculate the closing balance
        # set the latter transaction to happening before the first
        t = transactions[1]
        day_before_yesterday = yesterday - datetime.timedelta(days=1)
        t.date = day_before_yesterday
        t.save()
        
        homepage = HomePage(self.driver)
        transaction_list = homepage.transaction_list
        transactions = transaction_list.get_transactions()
        self.assertEqual(len(transactions), 2)
        
        t = transactions[0]
        self.assertEqual(t.date, day_before_yesterday)
        self.assertEqual(t.size, 1000)
        self.assertEqual(t.description, 'pay day')
        self.assertEqual(t.balance, '£1,000.00')
        
        t = transactions[1]
        self.assertEqual(t.date, yesterday)
        self.assertEqual(t.size, 500)
        self.assertEqual(t.description, 'dividends received')
        self.assertEqual(t.balance, '£1,500.00')
        
        # change transaction size
        t = transactions[0]
        t.size = 2000
        t.save()
        
        transactions = self.get_transactions()
        self.assertEqual(len(transactions), 2)
        
        t = transactions[0]
        self.assertEqual(t.date, day_before_yesterday)
        self.assertEqual(t.size, 2000)
        self.assertEqual(t.description, 'pay day')
        self.assertEqual(t.balance, '£2,000.00')
        
        t = transactions[1]
        self.assertEqual(t.date, yesterday)
        self.assertEqual(t.size, 500)
        self.assertEqual(t.description, 'dividends received')
        self.assertEqual(t.balance, '£2,500.00')


class TestTransactionModification(TransactionalTest):
        
    def test(self):

        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        tomorrow = today + datetime.timedelta(days=1)
        day_before_yesterday = yesterday - datetime.timedelta(days=1)

        self.create_transaction(yesterday, 1, 'a')
        self.create_transaction(today, 2, 'b')
        self.create_transaction(tomorrow, 3, 'c')

        transactions = self.get_transactions()

        t = transactions[0]
        self.assertEqual(t.description, 'a')
        self.assertEqual(t.balance, '£1.00')

        t = transactions[1]
        self.assertEqual(t.description, 'b')
        self.assertEqual(t.balance, '£3.00')
        
        t = transactions[2]
        self.assertEqual(t.description, 'c')
        self.assertEqual(t.balance, '£6.00')

        t.date = yesterday
        t.save()

        transactions = self.get_transactions()
        t = transactions[1]

        self.assertEqual(t.description, 'c')
        self.assertEqual(t.date, yesterday)
        self.assertEqual(t.size, 3)
        self.assertEqual(t.balance, '£4.00')

        t.date = day_before_yesterday
        t.save()

        transactions = self.get_transactions()
        
        t = transactions[0]
        self.assertEqual(t.description, 'c')
        self.assertEqual(t.date, day_before_yesterday)
        self.assertEqual(t.size, 3)
        self.assertEqual(t.balance, '£3.00')

        t = transactions[1]
        self.assertEqual(t.description, 'a')
        self.assertEqual(t.date, yesterday)
        self.assertEqual(t.size, 1)
        self.assertEqual(t.balance, '£4.00')

        t = transactions[2]
        self.assertEqual(t.description, 'b')
        self.assertEqual(t.date, today)
        self.assertEqual(t.size, 2)
        self.assertEqual(t.balance, '£6.00')


        
class TestTransactionDeletion(TransactionalTest):

    def test(self):

        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        tomorrow = today + datetime.timedelta(days=1)
        day_before_yesterday = yesterday - datetime.timedelta(days=1)

        self.create_transaction(yesterday, 1, 'a')
        self.create_transaction(today, 2, 'b')
        self.create_transaction(tomorrow, 3, 'c')

        transactions = self.get_transactions()
        t = transactions[1]
        t.delete()

        transactions = self.get_transactions()
        t = transactions[0]
        self.assertEqual(t.description, 'a')
        self.assertEqual(t.date, yesterday)
        self.assertEqual(t.size, 1)
        self.assertEqual(t.balance, '£1.00')

        t = transactions[1]
        self.assertEqual(t.description, 'c')
        self.assertEqual(t.date, tomorrow)
        self.assertEqual(t.size, 3)
        self.assertEqual(t.balance, '£4.00')

        
class TestDateSelection(TransactionalTest):

    def test(self):
        today = datetime.date.today()
        last_month = today - datetime.timedelta(days=30)

        self.create_transaction(last_month, 100, 'a')
        self.create_transaction(today, -50, 'b')

        balance_chart = BalanceChart(self.driver)

        self.assertEqual(balance_chart.bars[0].balance, 100)
        self.assertEqual(balance_chart.bars[14].balance, 50)
        
        date_selector = DateSelector(self.driver)

        date_selector.start = last_month
        date_selector.end = last_month + datetime.timedelta(days=7)
        date_selector.submit()

        balance_chart = BalanceChart(self.driver)
        
