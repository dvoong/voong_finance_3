import datetime
from functional_tests.TestCase import TestCase
from functional_tests.HomePage import HomePage
from functional_tests.WelcomePage import WelcomePage

class TransactionalTest(TestCase):

    def setUp(self):
        self.create_user(email='voong.david@gmail.com', password='password')
        super().setUp()

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
        self.driver.get(self.live_server_url)
        welcome_page = WelcomePage(self.driver)
        welcome_page.login_user(email='voong.david@gmail.com', password='password')
        
        homepage = HomePage(self.driver)
        today = datetime.date.today()

        self.assertEqual(homepage.transaction_form.date_input.get_attribute('value'),
                         today.isoformat())

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
            number_int = int(tick.replace('£', '').replace(',', '').replace('.', ''))
            number_float = float(tick.replace('£', '').replace(',', '').replace('.', ''))
            self.assertTrue(tick.startswith('£'))
            self.assertEqual(number_int, number_float) # int numbers only
        
        ## creates another transaction before the first
        ## transaction - check balances calculted properly

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
        self.driver.get(self.live_server_url)
        welcome_page = WelcomePage(self.driver)
        welcome_page.login_user(email='voong.david@gmail.com', password='password')

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
        self.driver.get(self.live_server_url)
        welcome_page = WelcomePage(self.driver)
        welcome_page.login_user(email='voong.david@gmail.com', password='password')

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

class TestRepeatTransactions(TestCase):

    def setUp(self):
        super().setUp()
        self.user = self.create_user('voong.david@gmail.com', 'password')

    def test(self):

        today = datetime.date.today()
        
        self.driver.get(self.live_server_url)
        welcome_page = WelcomePage(self.driver)
        welcome_page.login_user('voong.david@gmail.com', 'password')

        homepage = HomePage(self.driver)
        transaction_form = homepage.transaction_form
        transaction_form.date = today
        transaction_form.transaction_size = -10
        transaction_form.description = 'phone contract'
        transaction_form.repeat_checkbox.click()
        transaction_form.repeat_options.close()
        transaction_form.submit()

        homepage = HomePage(self.driver)
        transactions = homepage.transaction_list.get_transactions()

        self.assertEqual(len(transactions), 3)
        
        t = transactions[0]
        self.assertEqual(t.date, today)
        self.assertEqual(t.size, -10)
        self.assertEqual(t.description, 'phone contract')
        self.assertEqual(t.balance, '£-10.00')
        
        t = transactions[1]
        self.assertEqual(t.date, today + datetime.timedelta(days=7))
        self.assertEqual(t.size, -10)
        self.assertEqual(t.description, 'phone contract')
        self.assertEqual(t.balance, '£-20.00')
        
        t = transactions[2]
        self.assertEqual(t.date, today + datetime.timedelta(days=14))
        self.assertEqual(t.size, -10)
        self.assertEqual(t.description, 'phone contract')
        self.assertEqual(t.balance, '£-30.00')

        
class TestCustomRepeatTransaction(TestCase):

    def setUp(self):
        super().setUp()
        self.user = self.create_user('voong.david@gmail.com', 'password')

    def test_never_ends(self):

        today = datetime.date.today()
        
        self.driver.get(self.live_server_url)
        welcome_page = WelcomePage(self.driver)
        welcome_page.login_user('voong.david@gmail.com', 'password')

        homepage = HomePage(self.driver)
        transaction_form = homepage.transaction_form
        transaction_form.date = today
        transaction_form.transaction_size = -10
        transaction_form.description = 'phone contract'
        transaction_form.repeat_checkbox.click()

        repeat_options = transaction_form.repeat_options
        repeat_options.close()
        
        transaction_form.submit()
        
        homepage = HomePage(self.driver)
        transactions = homepage.transaction_list.get_transactions()

        self.assertEqual(len(transactions), 3)
        
        t = transactions[0]
        self.assertEqual(t.date, today)
        self.assertEqual(t.size, -10)
        self.assertEqual(t.description, 'phone contract')
        self.assertEqual(t.balance, '£-10.00')
        
        t = transactions[1]
        self.assertEqual(t.date, today + datetime.timedelta(days=7))
        self.assertEqual(t.size, -10)
        self.assertEqual(t.description, 'phone contract')
        self.assertEqual(t.balance, '£-20.00')
        
        t = transactions[2]
        self.assertEqual(t.date, today + datetime.timedelta(days=14))
        self.assertEqual(t.size, -10)
        self.assertEqual(t.description, 'phone contract')
        self.assertEqual(t.balance, '£-30.00')

    def test_ends_after_2_occurrences(self):

        today = datetime.date.today()
        
        self.driver.get(self.live_server_url)
        welcome_page = WelcomePage(self.driver)
        welcome_page.login_user('voong.david@gmail.com', 'password')

        homepage = HomePage(self.driver)
        transaction_form = homepage.transaction_form
        transaction_form.date = today
        transaction_form.transaction_size = -10
        transaction_form.description = 'phone contract'
        transaction_form.repeat_checkbox.click()

        repeat_options = transaction_form.repeat_options
        repeat_options.select('ends_after_#_occurrences')
        repeat_options.set_n_occurrences(2)
        repeat_options.close()
        
        transaction_form.submit()
        
        homepage = HomePage(self.driver)
        transactions = homepage.transaction_list.get_transactions()

        self.assertEqual(len(transactions), 2)
        
        t = transactions[0]
        self.assertEqual(t.date, today)
        self.assertEqual(t.size, -10)
        self.assertEqual(t.description, 'phone contract')
        self.assertEqual(t.balance, '£-10.00')
        
        t = transactions[1]
        self.assertEqual(t.date, today + datetime.timedelta(days=7))
        self.assertEqual(t.size, -10)
        self.assertEqual(t.description, 'phone contract')
        self.assertEqual(t.balance, '£-20.00')

    def test_monthly_transactions(self):

        start = datetime.date(2018, 4, 1)
        end = datetime.date(2018, 7, 1)
        
        self.driver.get(self.live_server_url)
        welcome_page = WelcomePage(self.driver)
        welcome_page.login_user('voong.david@gmail.com', 'password')

        self.driver.get('{}/home?start=2018-04-01&end=2018-08-01'.format(self.live_server_url))
                        
        homepage = HomePage(self.driver)
        transaction_form = homepage.transaction_form
        transaction_form.date = start
        transaction_form.transaction_size = -10
        transaction_form.description = 'phone contract'
        transaction_form.repeat_checkbox.click()

        repeat_options = transaction_form.repeat_options
        repeat_options.select('ends_on_date')
        repeat_options.set_frequency('monthly')
        repeat_options.set_end_date(end)
        repeat_options.close()

        transaction_form.submit()
        
        homepage = HomePage(self.driver)
        transactions = homepage.transaction_list.get_transactions()

        self.assertEqual(len(transactions), 4)
        
        t = transactions[0]
        self.assertEqual(t.date, start)
        self.assertEqual(t.size, -10)
        self.assertEqual(t.description, 'phone contract')
        self.assertEqual(t.balance, '£-10.00')
        
        t = transactions[1]
        self.assertEqual(t.date, datetime.date(2018, 5, 1))
        self.assertEqual(t.size, -10)
        self.assertEqual(t.description, 'phone contract')
        self.assertEqual(t.balance, '£-20.00')
        
        t = transactions[2]
        self.assertEqual(t.date, datetime.date(2018, 6, 1))
        self.assertEqual(t.size, -10)
        self.assertEqual(t.description, 'phone contract')
        self.assertEqual(t.balance, '£-30.00')
        
        t = transactions[3]
        self.assertEqual(t.date, datetime.date(2018, 7, 1))
        self.assertEqual(t.size, -10)
        self.assertEqual(t.description, 'phone contract')
        self.assertEqual(t.balance, '£-40.00')
