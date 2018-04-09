import datetime as dt
from functional_tests.TestCase import TestCase
from functional_tests.HomePage import HomePage
from functional_tests.WelcomePage import WelcomePage
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
        self.select = Select(self.element.find_element_by_tag_name('select'))

    def select(self, selection):
        self.select.select_by_value(selection)

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

    def test(self):

        home_page = HomePage(self.driver)
        home_page.create_transaction(date=dt.date(2018, 1, 1),
                                     size=10,
                                     description='a',
                                     repeats='weekly',
                                     ends={'how': 'never'})

        url = '{}/home?start={}&end={}'.format(self.live_server_url, '2018-01-01', '2018-01-15')
        self.driver.get(url)
        import time
        time.sleep(10)
        home_page = HomePage(self.driver)

        t_list = home_page.transaction_list
        transactions = t_list.get_transactions()

        import time
        time.sleep(30)
        t = transactions[1]
        t.delete()

        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.ID, 'repeat-transaction-deletion-prompt'))
        )

        prompt = RepeatTransactionDeletionPrompt(self.driver)
        prompt.select('delete_instance')
        prompt.submit()

        self.driver.get(url)
        home_page = HomePage(self.driver)
        t_list = home_page.transaction_list
        transactions = t_list.get_transactions()

        self.assertEqual(len(transactions), 2)

        t = transactions[0]
        self.assertEqual(t.date, dt.date(2018, 1, 1))

        t = transactions[1]
        self.assertEqual(t.date, dt.date(2018, 1, 15))
        
