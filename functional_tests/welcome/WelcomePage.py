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
        self.forgot_password_link = self.element.find_element_by_id('forgot-password-link')
        self.submit_button = self.element.find_element_by_id('submit-button')

    def login_user(self, email, password):

        self.email_input.send_keys(email)
        self.password_input.send_keys(password)
        self.submit_button.click()

    def click_forgot_password(self):
        self.forgot_password_link.click()

    def input_email(self, email):
        self.email_input.clear()
        self.email_input.send_keys(email)

    def input_password(self, password):
        self.password_input.clear()
        self.password_input.send_keys(password)

    def submit(self):
        self.submit_button.click()
        
class WelcomePage:

    url = '/welcome'

    def __init__(self, driver):
        self.registration_form = RegistrationForm(driver)
        self.login_form = LoginForm(driver)

    def login_user(self, email, password):
        self.login_form.login_user(email=email, password=password)
