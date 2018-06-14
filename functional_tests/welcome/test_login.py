from functional_tests.TestCase import TestCase
from functional_tests.homepage.HomePage import HomePage
from functional_tests.welcome.WelcomePage import LoginForm, RegistrationForm

class TestLogin(TestCase):

    def setUp(self):
        self.create_user(email='voong.david@gmail.com', password='password')
        super().setUp()
        self.login()

    def login(self):
        self.driver.get(self.live_server_url)
        login_form = LoginForm(self.driver)
        login_form.email_input.send_keys('voong.david@gmail.com')
        login_form.password_input.send_keys('password')
        login_form.submit_button.click()

    def test(self):
        homepage = HomePage(self.driver)

        
class TestSignOut(TestCase):
        
    def test(self):
        self.driver.get(self.live_server_url)

        registration_form = RegistrationForm(self.driver)
        registration_form.email_input.send_keys('voong.david@gmail.com')
        registration_form.password_input.send_keys('password')
        registration_form.password_check_input.send_keys('password')
        registration_form.submit_button.click()

        homepage = HomePage(self.driver)

        menu = homepage.menu
        menu.sign_out_button.click()
        self.assertEqual(self.driver.title, 'Welcome')
        
