from functional_tests.WelcomePage import RegistrationForm, LoginForm
from functional_tests.HomePage import HomePage
from functional_tests.TestCase import TestCase

class TestRegistration(TestCase):

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
