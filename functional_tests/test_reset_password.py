from django.core import mail
from functional_tests.welcome.WelcomePage import RegistrationForm, LoginForm
from functional_tests.TestCase import TestCase

class ResetPasswordFormRequest:

    def __init__(self, driver):

        self.driver = driver
        self.element = driver.find_element_by_id('password-reset-request-form')
        self.email_input = self.element.find_element_by_css_selector('input[name="email"]')

    def input_email(self, email):
        self.email_input.clear()
        self.email_input.send_keys(email)

class TestPasswordReset(TestCase):

    def setUp(self):
        super().setUp()
        self.create_user(email='voong.david@gmail.com', password='password')
        
    def test(self):

        self.driver.get(self.live_server_url)
        login_form = LoginForm(self.driver)
        login_form.click_forgot_password()

        self.assertEqual(self.driver.current_url, '{}/reset-password'.format(self.live_server_url))

        reset_password_form = ResetPasswordFormRequest(self.driver)
        reset_password_form.input_email('voong.david@gmail.com')
        reset_password_form.submit()

        self.assertEqual(len(mail.outbox), 1)
        
        reset_email = ResetEmail(mail.outbox[0])
        self.assertEqual(reset_email.subject, 'Password reset')
        self.assertEqual(reset_email.sender, 'admin@voong-finance.co.uk')

        self.driver.get(reset_email.reset_link)

        reset_password_form = ResetPasswordForm(self.driver)
        reset_password_form.input_password('password2')
        reset_password_form.input_password_confirmation('password2')
        reset_password_form.submit()

        self.assertEqual(self.driver.current_url, '{}/home'.format(self.live_server_url))

        home_page = HomePage(self.driver)
        home_page.logout()

        login_form = LoginForm(self.driver)
        login_form.input_email('voong.david@gmail.com')
        login_form.input_password('password2')
        login_form.submit()

        self.assertEqual(self.driver.current_url, '{}/home'.format(self.live_server_url))
