import datetime as dt

strptime = dt.datetime.strptime

class RepeatTransaction:

    CLASS_NAME = 'repeat-transaction'
    FORM_ID = 'repeat-transaction-update-form-{id}'
    SAVE_BUTTON_ID = 'repeat-transaction-save-button-{id}'

    def __init__(self, element, driver):

        self.element = element
        self.driver = driver
        self.id = int(self.element.get_attribute('id'))
        self.form = self.driver.find_element_by_id(self.FORM_ID.format(id=self.id))
        self.save_button = self.driver.find_element_by_id(self.SAVE_BUTTON_ID.format(id=self.id))

    @property
    def start_date(self):
        element = self.element.find_element_by_css_selector('input[name="start_date"]')
        value = element.get_attribute('value')
        date = strptime(value, '%Y-%m-%d').date()
        return date

    @start_date.setter
    def start_date(self, date):
        element = self.element.find_element_by_css_selector('input[name="start_date"]')
        keys = '{:02d}{:02d}{}'.format(date.day, date.month, date.year)        
        element.send_keys(keys)

    @property
    def size(self):
        element = self.element.find_element_by_css_selector('input[name="size"]')
        value = element.get_attribute('value')
        print(value)
        value = float(value.replace('£', ''))
        return value

    @size.setter
    def size(self, size):
        element = self.element.find_element_by_css_selector('input[name="size"]')
        element.clear()
        element.send_keys(size)

    @property
    def description(self):
        element = self.element.find_element_by_css_selector('input[name="description"]')
        value = element.get_attribute('value')
        return value

    @description.setter
    def description(self, description):
        element = self.element.find_element_by_css_selector('input[name="description"]')
        element.clear()
        element.send_keys(description)

    @property
    def frequency(self):
        element = self.element.find_element_by_css_selector('input[name="frequency"]')
        value = element.get_attribute('value')
        return value

    @property
    def ends(self):
        element = self.element.find_element_by_css_selector('input[name="ends"]')
        value = element.get_attribute('value')
        if value == 'never':
            return value
        else:
            date = strptime(value, '%Y-%m-%d').date()
            return date

    def save(self):
        self.save_button.click()
