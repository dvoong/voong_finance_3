import datetime
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

strptime = datetime.datetime.strptime

class HomePage:

    def __init__(self, driver):

        self.driver = driver
        self.balance_chart = BalanceChart(driver)
        self.transaction_form = TransactionForm(driver)
        self.menu = Menu(driver)
        self.transaction_list = TransactionList(driver)
        self.date_selector = DateSelector(driver.find_element_by_id('date-selector'))
        self.week_forward_button = driver.find_element_by_id('week-forward-button')
        self.week_backward_button = driver.find_element_by_id('week-backward-button')
        self.date_range = self.get_date_range()

    def create_transaction(self, update=True, *args, **kwargs):
        self.transaction_form.create_transaction(*args, **kwargs)
        if update == True:
            self.__init__(self.driver)

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

    def create_transaction(self, date, size, description=""):
        self.date = date
        self.transaction_size_input.send_keys(size)
        self.description_input.send_keys(description)
        self.submit_button.click()

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
        WebDriverWait(self.driver, 5).until(
            EC.invisibility_of_element_located((By.ID, 'repeat-options-div'))
        )
        self.submit_button.click()

        
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
        WebDriverWait(self.element, 5).until(
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
        self.ends_after_n_occurrences = self.element.find_element_by_id('ends-after-n-occurrences')
        self.n_occurrences_input =self.element.find_element_by_id('n-occurrences-input')
        self.ends_on_date = self.element.find_element_by_id('ends-on-date')
        self.end_date_input = self.element.find_element_by_id('ends-on-date-input')
        self.never_ends = self.element.find_element_by_id('never-ends')
        self.frequency_input = Select(self.element.find_element_by_id('frequency-input'))

    def close(self):
        try:
            element = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.ID, "repeat-options-close-button"))
            )
            self.close_button.click()
        except:
            pass

    def select(self, option):
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.ID, 'ends-after-n-occurrences'))
        )
        if option == 'ends_after_#_occurrences':
            self.ends_after_n_occurrences.click()
        elif option == 'ends_on_date':
            self.ends_on_date.click()
        elif option == 'never':
            self.never_ends.click()

    def set_n_occurrences(self, occurrences):
        self.n_occurrences_input.clear()
        self.n_occurrences_input.send_keys(occurrences)
        
    def set_end_date(self, date):
        keys = '{:02d}{:02d}{}'.format(date.day, date.month, date.year)        
        self.end_date_input.send_keys(keys)

    def set_frequency(self, frequency):
        self.frequency_input.select_by_value(frequency)
