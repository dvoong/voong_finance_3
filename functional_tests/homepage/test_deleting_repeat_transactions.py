import datetime as dt
from functional_tests.TestCase import TestCase
from functional_tests.homepage.HomePage import HomePage
from functional_tests.welcome.WelcomePage import WelcomePage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

strptime = dt.datetime.strptime

class RepeatTransactionDeletionPrompt:

    id = 'repeat-transaction-deletion-prompt'

    def __init__(self, driver):

        self.driver = driver
        self.element = driver.find_element_by_id(self.id)
        id_ = 'repeat-transaction-deletion-delete-button'
        self.submit_button = self.element.find_element_by_id(id_)

    def select(self, selection):
        css_selector = 'input[name="delete_how"][value="{}"]'.format(selection)
        element = self.element.find_element_by_css_selector(css_selector)
        element.click()

    def submit(self):
        self.submit_button.click()
        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.ID, self.id)))

    def cancel(self):
        self.cancel_button.click()
        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.ID, self.id)))

        
class TestRepeatTransactionDeletion(TestCase):

    def setUp(self):
        super().setUp()
        self.create_user(email='voong.david@gmail.com', password='password')
        self.driver.get(self.live_server_url)
        welcome_page = WelcomePage(self.driver)
        welcome_page.login_user(email='voong.david@gmail.com', password='password')

    def tearDown(self):
        self.driver.close()
        
    def test_this_transaction_only_deletion(self):

        home_page = HomePage(self.driver)
        home_page.create_transaction(date=dt.date(2018, 1, 1),
                                     size=10,
                                     description='a',
                                     repeats='weekly',
                                     ends={'how': 'never_ends'})
        home_page.create_transaction(date=dt.date(2018, 1, 9),
                                     size=5,
                                     description='b')

        url = '{}/home?start={}&end={}'.format(self.live_server_url, '2018-01-01', '2018-01-15')
        self.driver.get(url)
        home_page = HomePage(self.driver)

        t_list = home_page.transaction_list
        transactions = t_list.get_transactions()

        t = transactions[1]
        t.delete()

        ###
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.ID, 'repeat-transaction-deletion-prompt'))
        )

        prompt = RepeatTransactionDeletionPrompt(self.driver)
        prompt.select('delete_only_this_transaction')
        prompt.submit()
        
        ### put this in the transaction class
        
        self.driver.get(url)
        home_page = HomePage(self.driver)
        t_list = home_page.transaction_list
        transactions = t_list.get_transactions()

        self.assertEqual(len(transactions), 3)

        t = transactions[0]
        self.assertEqual(t.date, dt.date(2018, 1, 1))

        t = transactions[1]
        self.assertEqual(t.date, dt.date(2018, 1, 9))
        self.assertEqual('£15.00', t.balance)

        t = transactions[2]
        self.assertEqual(t.date, dt.date(2018, 1, 15))
        self.assertEqual('£25.00', t.balance)
        
    def test_this_transaction_and_future_transactions_deletion(self):

        url = '{}/home?start={}&end={}'.format(self.live_server_url, '2018-01-01', '2018-01-15')
        self.driver.get(url)
        home_page = HomePage(self.driver)
        home_page.create_transaction(date=dt.date(2018, 1, 1),
                                     size=10,
                                     description='a',
                                     repeats='weekly',
                                     ends={'how': 'never_ends'})

        home_page.create_transaction(date=dt.date(2018, 1, 9),
                                     size=5,
                                     description='b')

        url = '{}/home?start={}&end={}'.format(self.live_server_url, '2018-01-01', '2018-01-15')
        self.driver.get(url)
        home_page = HomePage(self.driver)

        t_list = home_page.transaction_list
        transactions = t_list.get_transactions()

        t = transactions[1]
        t.delete()

        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.ID, 'repeat-transaction-deletion-prompt'))
        )

        prompt = RepeatTransactionDeletionPrompt(self.driver)
        prompt.select('delete_this_transaction_and_future_transactions')
        prompt.submit()

        self.driver.get(url)
        home_page = HomePage(self.driver)
        t_list = home_page.transaction_list
        transactions = t_list.get_transactions()
        
        self.assertEqual(len(transactions), 2)

        t = transactions[0]
        self.assertEqual(t.date, dt.date(2018, 1, 1))
        
        t = transactions[1]
        self.assertEqual(t.date, dt.date(2018, 1, 9))
        self.assertEqual('£15.00', t.balance)

        url = '{}/home?start={}&end={}'.format(self.live_server_url, '2018-01-01', '2018-01-22')
        self.driver.get(url)
        home_page = HomePage(self.driver)

        t_list = home_page.transaction_list
        transactions = t_list.get_transactions()

        self.assertEqual(len(transactions), 2)

        t = transactions[0]
        self.assertEqual(t.date, dt.date(2018, 1, 1))
        
        t = transactions[1]
        self.assertEqual(t.date, dt.date(2018, 1, 9))
        self.assertEqual('£15.00', t.balance)
        
    def test_deletion_of_all_transactions_of_this_type(self):

        url = '{}/home?start={}&end={}'.format(self.live_server_url, '2018-01-01', '2018-01-15')
        self.driver.get(url)
        home_page = HomePage(self.driver)
        home_page.create_transaction(date=dt.date(2018, 1, 1),
                                     size=10,
                                     description='a',
                                     repeats='weekly',
                                     ends={'how': 'never_ends'})
        home_page.create_transaction(date=dt.date(2018, 1, 9),
                                     size=5,
                                     description='b')

        url = '{}/home?start={}&end={}'.format(self.live_server_url, '2018-01-01', '2018-01-15')
        self.driver.get(url)
        home_page = HomePage(self.driver)

        t_list = home_page.transaction_list
        transactions = t_list.get_transactions()

        t = transactions[1]
        t.delete()

        WebDriverWait(self.driver, 20).until(
            EC.visibility_of_element_located((By.ID, 'repeat-transaction-deletion-prompt'))
        )

        prompt = RepeatTransactionDeletionPrompt(self.driver)
        prompt.select('all_transactions_of_this_type')
        prompt.submit()

        self.driver.get(url)
        home_page = HomePage(self.driver)
        t_list = home_page.transaction_list
        transactions = t_list.get_transactions()

        self.assertEqual(len(transactions), 1)
        
        t = transactions[0]
        self.assertEqual(t.date, dt.date(2018, 1, 9))
        self.assertEqual(t.description, 'b')
        self.assertEqual('£5.00', t.balance)

        url = '{}/home?start={}&end={}'.format(self.live_server_url, '2018-01-01', '2018-01-22')
        self.driver.get(url)
        home_page = HomePage(self.driver)

        t_list = home_page.transaction_list
        transactions = t_list.get_transactions()

        self.assertEqual(len(transactions), 1)
        
        t = transactions[0]
        self.assertEqual(t.date, dt.date(2018, 1, 9))
        self.assertEqual('£5.00', t.balance)

        rts = home_page.get_repeat_transactions()
        self.assertEqual(len(rts), 0)
        

class RepeatTransactionUpdatePrompt:

    id = 'repeat-transaction-update-prompt'

    def __init__(self, driver):

        self.driver = driver
        self.element = driver.find_element_by_id(self.id)
        id_ = 'repeat-transaction-update-update-button'
        self.submit_button = self.element.find_element_by_id(id_)

    def select(self, selection):
        css_selector = 'input[name="update_how"][value="{}"]'.format(selection)
        element = self.element.find_element_by_css_selector(css_selector)
        element.click()

    def submit(self):
        self.submit_button.click()
        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.ID, self.id)))

    def cancel(self):
        self.cancel_button.click()
        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.ID, self.id)))

        
class TestRepeatTransactionUpdate(TestCase):

    def setUp(self):
        super().setUp()
        self.create_user(email='voong.david@gmail.com', password='password')
        self.driver.get(self.live_server_url)
        welcome_page = WelcomePage(self.driver)
        welcome_page.login_user(email='voong.david@gmail.com', password='password')

    def tearDown(self):
        self.driver.close()
        
    def test_this_transaction_only_update(self):

        home_page = HomePage(self.driver)
        home_page.create_transaction(date=dt.date(2018, 1, 1),
                                     size=10,
                                     description='a',
                                     repeats='weekly',
                                     ends={'how': 'never_ends'})
        home_page.create_transaction(date=dt.date(2018, 1, 9),
                                     size=5,
                                     description='b')

        url = '{}/home?start={}&end={}'.format(self.live_server_url, '2018-01-01', '2018-01-15')
        self.driver.get(url)
        home_page = HomePage(self.driver)

        t_list = home_page.transaction_list
        transactions = t_list.get_transactions()

        self.assertEqual(len(transactions), 4)

        t = transactions[0]
        self.assertEqual(t.date, dt.date(2018, 1, 1))
        self.assertEqual(t.description, 'a')

        t = transactions[1]
        self.assertEqual(t.date, dt.date(2018, 1, 8))
        self.assertEqual(t.description, 'a')
        
        t = transactions[1]
        t.description = 'c'
        t.save()

        ###
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.ID, 'repeat-transaction-update-prompt'))
        )

        prompt = RepeatTransactionUpdatePrompt(self.driver)
        prompt.select('update_only_this_transaction')
        prompt.submit()
        
        ### put this in the transaction class
        
        self.driver.get(url)
        home_page = HomePage(self.driver)
        t_list = home_page.transaction_list
        transactions = t_list.get_transactions()

        self.assertEqual(len(transactions), 4)

        t = transactions[0]
        self.assertEqual(t.date, dt.date(2018, 1, 1))
        self.assertEqual(t.description, 'a')
        self.assertEqual('£10.00', t.balance)

        t = transactions[1]
        self.assertEqual(t.date, dt.date(2018, 1, 8))
        self.assertEqual(t.description, 'c')
        self.assertEqual('£20.00', t.balance)

        t = transactions[2]
        self.assertEqual(t.date, dt.date(2018, 1, 9))
        self.assertEqual('£25.00', t.balance)
        self.assertEqual(t.description, 'b')

        t = transactions[3]
        self.assertEqual(t.date, dt.date(2018, 1, 15))
        self.assertEqual('£35.00', t.balance)
        self.assertEqual(t.description, 'a')
        
    def test_update_repeat_transaction_description_only(self):

        url = '{}/home?start={}&end={}'.format(self.live_server_url, '2018-01-01', '2018-01-15')
        self.driver.get(url)
        home_page = HomePage(self.driver)
        home_page.create_transaction(date=dt.date(2018, 1, 1),
                                     size=10,
                                     description='a',
                                     repeats='weekly',
                                     ends={'how': 'never_ends'})
        home_page.create_transaction(date=dt.date(2018, 1, 9),
                                     size=5,
                                     description='b')

        home_page = HomePage(self.driver)

        t_list = home_page.transaction_list
        transactions = t_list.get_transactions()

        self.assertEqual(len(transactions), 4)

        t = transactions[0]
        self.assertEqual(t.date, dt.date(2018, 1, 1))
        self.assertEqual(t.description, 'a')

        t = transactions[1]
        self.assertEqual(t.date, dt.date(2018, 1, 8))
        self.assertEqual(t.description, 'a')

        t = transactions[1]
        t.description = 'c'
        t.save()

        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.ID, 'repeat-transaction-update-prompt'))
        )

        prompt = RepeatTransactionUpdatePrompt(self.driver)
        prompt.select('update_this_transaction_and_future_transactions')
        prompt.submit()

        home_page = HomePage(self.driver)
        t_list = home_page.transaction_list
        transactions = t_list.get_transactions()

        self.assertEqual(len(transactions), 4)

        t = transactions[0]
        self.assertEqual(t.date, dt.date(2018, 1, 1))
        
        t = transactions[1]
        self.assertEqual(t.date, dt.date(2018, 1, 8))
        self.assertEqual('c', t.description)
        
        t = transactions[2]
        self.assertEqual(t.date, dt.date(2018, 1, 9))
        self.assertEqual('b', t.description)
        
        t = transactions[3]
        self.assertEqual(t.date, dt.date(2018, 1, 15))
        self.assertEqual('c', t.description)
        self.assertEqual('£35.00', t.balance)

        url = '{}/home?start={}&end={}'.format(self.live_server_url, '2018-01-01', '2018-01-22')
        self.driver.get(url)
        home_page = HomePage(self.driver)

        t_list = home_page.transaction_list
        transactions = t_list.get_transactions()

        self.assertEqual(len(transactions), 5)

        t = transactions[4]
        self.assertEqual(t.date, dt.date(2018, 1, 22))
        self.assertEqual('c', t.description)
        self.assertEqual('£45.00', t.balance)
 
    def test_update_repeat_transaction_date_only(self):

        url = '{}/home?start={}&end={}'.format(self.live_server_url, '2018-01-01', '2018-01-15')
        self.driver.get(url)
        home_page = HomePage(self.driver)
        home_page.create_transaction(date=dt.date(2018, 1, 1),
                                     size=10,
                                     description='a',
                                     repeats='weekly',
                                     ends={'how': 'never_ends'})
        home_page.create_transaction(date=dt.date(2018, 1, 9),
                                     size=5,
                                     description='b')

        home_page = HomePage(self.driver)
        t_list = home_page.transaction_list
        transactions = t_list.get_transactions()

        self.assertEqual(len(transactions), 4)

        t = transactions[0]
        self.assertEqual(t.date, dt.date(2018, 1, 1))
        self.assertEqual(t.description, 'a')

        t = transactions[1]
        self.assertEqual(t.date, dt.date(2018, 1, 8))
        self.assertEqual(t.description, 'a')

        t = transactions[1]
        t.date = dt.date(2018, 1, 7)
        t.save()
        
        url = '{}/home?start={}&end={}'.format(self.live_server_url, '2018-01-01', '2018-01-15')
        self.driver.get(url)
        home_page = HomePage(self.driver)
        t_list = home_page.transaction_list
        transactions = t_list.get_transactions()

        self.assertEqual(len(transactions), 4)

        t = transactions[0]
        self.assertEqual(t.date, dt.date(2018, 1, 1))
        
        t = transactions[1]
        self.assertEqual(t.date, dt.date(2018, 1, 7))
        self.assertEqual('a', t.description)
        
        t = transactions[2]
        self.assertEqual(t.date, dt.date(2018, 1, 9))
        self.assertEqual('b', t.description)
        
        t = transactions[3]
        self.assertEqual(t.date, dt.date(2018, 1, 15))
        self.assertEqual('a', t.description)
        self.assertEqual('£35.00', t.balance)

        url = '{}/home?start={}&end={}'.format(self.live_server_url, '2018-01-01', '2018-01-22')
        self.driver.get(url)
        home_page = HomePage(self.driver)

        t_list = home_page.transaction_list
        transactions = t_list.get_transactions()

        self.assertEqual(len(transactions), 5)

        t = transactions[4]
        self.assertEqual(t.date, dt.date(2018, 1, 22))
        self.assertEqual('a', t.description)
        self.assertEqual('£45.00', t.balance)

    def test_date_and_description_changed(self):

        home_page = HomePage(self.driver)
        home_page.create_transaction(date=dt.date(2018, 1, 1),
                                     size=10,
                                     description='a',
                                     repeats='weekly',
                                     ends={'how': 'never_ends'})
        home_page.create_transaction(date=dt.date(2018, 1, 9),
                                     size=5,
                                     description='b')

        url = '{}/home?start={}&end={}'.format(self.live_server_url, '2018-01-01', '2018-01-15')
        self.driver.get(url)
        home_page = HomePage(self.driver)

        t_list = home_page.transaction_list
        transactions = t_list.get_transactions()

        self.assertEqual(len(transactions), 4)

        t = transactions[0]
        self.assertEqual(t.date, dt.date(2018, 1, 1))
        self.assertEqual(t.description, 'a')

        t = transactions[1]
        self.assertEqual(t.date, dt.date(2018, 1, 8))
        self.assertEqual(t.description, 'a')
        
        t = transactions[1]
        t.date = dt.date(2018, 1, 7)
        t.description = 'c'
        t.save()
        
        self.driver.get(url)
        home_page = HomePage(self.driver)
        t_list = home_page.transaction_list
        transactions = t_list.get_transactions()

        self.assertEqual(len(transactions), 4)

        t = transactions[0]
        self.assertEqual(t.date, dt.date(2018, 1, 1))
        self.assertEqual(t.description, 'a')
        self.assertEqual('£10.00', t.balance)

        t = transactions[1]
        self.assertEqual(t.date, dt.date(2018, 1, 7))
        self.assertEqual(t.description, 'c')
        self.assertEqual('£20.00', t.balance)

        t = transactions[2]
        self.assertEqual(t.date, dt.date(2018, 1, 9))
        self.assertEqual('£25.00', t.balance)
        self.assertEqual(t.description, 'b')

        t = transactions[3]
        self.assertEqual(t.date, dt.date(2018, 1, 15))
        self.assertEqual('£35.00', t.balance)
        self.assertEqual(t.description, 'a')
        
    def test_update_repeat_transaction_description_only_all_transactions(self):

        url = '{}/home?start={}&end={}'.format(self.live_server_url, '2018-01-01', '2018-01-15')
        self.driver.get(url)
        home_page = HomePage(self.driver)
        home_page.create_transaction(date=dt.date(2018, 1, 1),
                                     size=10,
                                     description='a',
                                     repeats='weekly',
                                     ends={'how': 'never_ends'})
        home_page.create_transaction(date=dt.date(2018, 1, 9),
                                     size=5,
                                     description='b')

        home_page = HomePage(self.driver)

        t_list = home_page.transaction_list
        transactions = t_list.get_transactions()

        self.assertEqual(len(transactions), 4)

        t = transactions[0]
        self.assertEqual(t.date, dt.date(2018, 1, 1))
        self.assertEqual(t.description, 'a')

        t = transactions[1]
        self.assertEqual(t.date, dt.date(2018, 1, 8))
        self.assertEqual(t.description, 'a')

        t = transactions[1]
        t.description = 'c'
        t.save()

        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.ID, 'repeat-transaction-update-prompt'))
        )

        prompt = RepeatTransactionUpdatePrompt(self.driver)
        prompt.select('update_all_transactions_of_this_kind')
        prompt.submit()

        home_page = HomePage(self.driver)
        t_list = home_page.transaction_list
        transactions = t_list.get_transactions()

        self.assertEqual(len(transactions), 4)

        t = transactions[0]
        self.assertEqual(t.date, dt.date(2018, 1, 1))
        self.assertEqual('c', t.description)
        
        t = transactions[1]
        self.assertEqual(t.date, dt.date(2018, 1, 8))
        self.assertEqual('c', t.description)
        
        t = transactions[2]
        self.assertEqual(t.date, dt.date(2018, 1, 9))
        self.assertEqual('b', t.description)
        
        t = transactions[3]
        self.assertEqual(t.date, dt.date(2018, 1, 15))
        self.assertEqual('c', t.description)
        self.assertEqual('£35.00', t.balance)

        url = '{}/home?start={}&end={}'.format(self.live_server_url, '2018-01-01', '2018-01-22')
        self.driver.get(url)
        home_page = HomePage(self.driver)

        t_list = home_page.transaction_list
        transactions = t_list.get_transactions()

        self.assertEqual(len(transactions), 5)

        t = transactions[4]
        self.assertEqual(t.date, dt.date(2018, 1, 22))
        self.assertEqual('c', t.description)
        self.assertEqual('£45.00', t.balance)
