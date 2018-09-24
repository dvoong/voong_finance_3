import datetime
import pandas as pd
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from .RepeatTransaction import RepeatTransaction
from functional_tests.TestCase import wait_for

strptime = datetime.datetime.strptime

class HomePage:

    def __init__(self, driver):

        self.driver = driver
        self.balance_chart = BalanceChart(driver)
        self.transaction_form = TransactionForm(driver)
        self.menu = Menu(driver)
        self.transaction_list = TransactionList(driver)
        self.repeat_transactions_list = RepeatTransactionsList(driver)
        self.date_selector = DateSelector(driver.find_element_by_id('date-selector'))
        self.week_forward_button = driver.find_element_by_id('week-forward-button')
        self.week_backward_button = driver.find_element_by_id('week-backward-button')
        self.date_range = self.get_date_range()
        self.transactions_tab = driver.find_element_by_id('transactions-tab')
        self.repeat_transactions_tab = driver.find_element_by_id('repeat-transactions-tab')
        
    def create_transaction(self, update=True, *args, **kwargs):
        self.transaction_form.create_transaction(*args, **kwargs)
        if update == True:
            self.__init__(self.driver)

    def get_balances(self):
        values = [(b.date, b.balance) for b in self.balance_chart.bars]
        df_balances = pd.DataFrame(values, columns=['date', 'balance'])
        df_balances = df_balances.set_index('date')
        df_balances.index = pd.to_datetime(df_balances.index)
        return df_balances
            
    def move_date_range_forward(self, days=7):
        if days == 7:
            self.week_forward_button.click()
        else:
            raise Exception('unknown days attribute: {}'.format(days))

    def move_date_range_backward(self, days=7):
        if days == 7:
            self.week_backward_button.click()
        else:
            raise Exception('unknown days attribute: {}'.format(days))

    def get_date_range(self):
        start_input = self.driver.find_element_by_css_selector('#date-selector #start-input')
        end_input = self.driver.find_element_by_css_selector('#date-selector #end-input')
        start = strptime(start_input.get_attribute('value'), '%Y-%m-%d').date()
        end = strptime(end_input.get_attribute('value'), '%Y-%m-%d').date()
        return [start, end]

    def show_repeat_transactions_view(self):
        self.repeat_transactions_tab.click()
        WebDriverWait(self.driver, 60).until(
            EC.visibility_of_element_located((By.ID, 'repeat-transactions'))
        )

    def show_transactions_view(self):
        self.transactions_tab.click()
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'transactions'))
        )

    def get_repeat_transactions(self):
        rts = []
        class_name = RepeatTransaction.CLASS_NAME
        for e in self.driver.find_elements_by_css_selector('.{}'.format(class_name)):
            rts.append(RepeatTransaction(e, self.driver))
        return rts

    def wait_for_repeat_transaction_prompt(self, timeout):
        wait_for(RepeatTransaction.PROMPT_ID, driver=self.driver, timeout=timeout, by='id')

    def get_transactions(self):
        return self.transaction_list.get_transactions()

    def reload(self):
        self.__init__(self.driver)

class TransactionForm:

    def __init__(self, driver):

        self.driver = driver
        self.element = driver.find_element_by_id('transaction-form')
        css_selector = '#date-input[form="transaction-form"]'
        self.date_input = driver.find_element_by_css_selector(css_selector)
        css_selector = '#transaction-size-input[form="transaction-form"]'
        self.transaction_size_input = driver.find_element_by_css_selector(css_selector)
        css_selector = '#description-input[form="transaction-form"]'
        self.description_input = driver.find_element_by_css_selector(css_selector)
        css_selector = '#submit-button[form="transaction-form"]'
        self.submit_button = driver.find_element_by_css_selector(css_selector)
        self.repeat_checkbox = driver.find_element_by_id('repeat-checkbox')
        self.repeat_options = RepeatOptions(self.driver)

    def create_transaction(
            self,
            date,
            size,
            description="",
            repeats='does_not_repeat',
            ends=None,
            steps=None,
            frequency=None):
        
        self.date = date
        self.transaction_size_input.send_keys(size)
        self.description_input.send_keys(description)
        if repeats == 'does_not_repeat':
            if self.repeat_checkbox.is_selected():
                self.repeat_checkbox.click()
            self.submit_button.click()
        else:
            if not self.repeat_checkbox.is_selected():
                self.repeat_checkbox.click()
            self.set_repeat_frequency(repeats, steps)
            self.set_end_criteria(ends)
            self.repeat_options.submit()

    @property
    def date(self):
        return strptime(self.date_input.get_attribute('value'), '%Y-%m-%d').date()

    @date.setter
    def date(self, date):
        keys = '{:02d}{:02d}{}'.format(date.day, date.month, date.year)        
        self.date_input.send_keys(keys)

    @property
    def transaction_size(self):
        return float(self.transaction_size_input.get_attribute('value'))

    @transaction_size.setter
    def transaction_size(self, transaction_size):
        self.transaction_size_input.send_keys(transaction_size)

    @property
    def description(self):
        return float(self.description_input.get_attribute('value'))

    @description.setter
    def description(self, description):
        self.description_input.send_keys(description)

    def submit(self):
        WebDriverWait(self.driver, 10).until(
            EC.invisibility_of_element_located((By.ID, 'repeat-options-div'))
        )
        self.submit_button.click()

    def set_repeat_frequency(self, frequency, steps=1):
        self.repeat_options.set_frequency(frequency, steps)

    def set_end_criteria(self, ends):
        self.repeat_options.set_end_criteria(ends)
        
class Menu:

    def __init__(self, driver):
        self.element = driver.find_element_by_id('menu')
        self.sign_out_button = driver.find_element_by_id('sign-out')

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
        WebDriverWait(self.element, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.bar'))
        )
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
        # WebDriverWait(self.element, 10).until(
        #     lambda x: self.save_button.is_displayed
        # )
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

class RepeatOptions:

    def __init__(self, driver):

        self.driver = driver
        self.element = driver.find_element_by_id('repeat-options-div')
        self.close_button = driver.find_element_by_id('repeat-options-close-button')
        self.submit_button = driver.find_element_by_id('repeat-options-submit-button')
        self.ends_after_n_transactions = self.element.find_element_by_id('ends-after-n-transactions')
        self.n_transactions_input =self.element.find_element_by_id('n-transactions-input')
        self.ends_on_date = self.element.find_element_by_id('ends-on-date')
        self.end_date_input = self.element.find_element_by_id('ends-on-date-input')
        self.never_ends = self.element.find_element_by_id('never-ends')
        self.frequency_input = Select(self.element.find_element_by_id('frequency-input'))
        self.steps_input = self.element.find_element_by_id('steps-input')

    def submit(self):
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "repeat-options-submit-button"))
        )
        self.submit_button.click()
        WebDriverWait(self.driver, 10).until(
            EC.invisibility_of_element_located((By.ID, "repeat-options-submit -button"))
        )

    def select(self, option):
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'ends-after-n-transactions'))
        )
        if option == 'ends_after_#_transactions':
            self.ends_after_n_transactions.click()
        elif option == 'ends_on_date':
            self.ends_on_date.click()
        elif option == 'never':
            self.never_ends.click()

    def set_n_transactions(self, transactions):
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, self.n_transactions_input.get_attribute('id')))
        )
        self.n_transactions_input.clear()
        self.n_transactions_input.send_keys(transactions)
        
    def set_end_date(self, date):
        keys = '{:02d}{:02d}{}'.format(date.day, date.month, date.year)        
        self.end_date_input.send_keys(keys)

    def set_frequency(self, frequency, steps=None):
        self.frequency_input.select_by_value(frequency)
        WebDriverWait(self.driver, 60).until(
            EC.visibility_of_element_located((By.ID, self.steps_input.get_attribute('id')))
        )
        if steps is not None:
            self.steps_input.send_keys(steps)

    def set_end_criteria(self, ends):
        self.select(ends['how'])
        if ends['how'] == 'never_ends':
            pass
        elif ends['how'] == 'ends_after_#_transactions':
            self.set_n_transactions(ends['when'])
        elif ends['how'] == 'ends_on_date':
            self.set_end_date(ends['when'])
        else:
            raise Exception('unrecognised end criteria: {}'.format(ends))

class RepeatTransactionsList:

    def __init__(self, driver):

        self.driver = driver
        self.element = driver.find_element_by_id('repeat-transactions')
        self.table = self.element.find_element_by_tag_name('table')

    def assert_in(self, date, size, description, repeats, ends):
        x = (date, size, description, repeats, ends)
        assert len(list(filter(lambda y: y == x, self.items))) > 0

    @property
    def items(self):
        rows = self.table.find_elements_by_css_selector('.repeat-transaction')
        items = []
        for row in rows:
            tds = row.find_elements_by_tag_name('td')
            date_input = tds[0].find_element_by_tag_name('input')
            date = strptime(date_input.get_attribute('value'), '%Y-%m-%d').date()
            size_input = tds[1].find_element_by_tag_name('input')
            size = float(size_input.get_attribute('value').replace('£', ''))
            description_input = tds[2].find_element_by_tag_name('input')
            description = description_input.get_attribute('value')
            repeats_input = tds[3].find_element_by_tag_name('input')
            repeats = repeats_input.get_attribute('value')
            ends_input = tds[4].find_element_by_tag_name('input')
            ends = ends_input.get_attribute('value')
            repeat_transaction = {
                'date': date,
                'size': size,
                'description': description,
                'repeats': repeats,
                'ends': ends
            }

            items.append(repeat_transaction)
        return items
