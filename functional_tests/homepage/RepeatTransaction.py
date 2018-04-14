import datetime as dt

strptime = dt.datetime.strptime

class RepeatTransaction:

    CLASS_NAME = 'repeat-transaction'

    def __init__(self, element):

        self.element = element

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

    @property
    def description(self):
        element = self.element.find_element_by_css_selector('input[name="description"]')
        value = element.get_attribute('value')
        return value

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

    
