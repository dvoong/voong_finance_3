from functional_tests.TestCase import TestCase
from functional_tests.homepage.HomePage import HomePage
from functional_tests.welcome.WelcomePage import LoginForm, RegistrationForm

class TestLogin(TestCase):

    def setUp(self):
        self.create_user(email='voong.david@gmail.com', password='password')
        super().setUp()
        self.sign_in('voong.david@gmail.com', password='password')

    def test(self):
        homepage = HomePage(self.driver)

        
class TestSignOut(TestCase):

    def setUp(self):
        super().setUp()
        self.create_user(email='voong.david@gmail.com', password='password')
        self.sign_in('voong.david@gmail.com', password='password')
        
    def test(self):

        self.driver.get(self.live_server_url)
        homepage = HomePage(self.driver)

        menu = homepage.menu
        menu.sign_out_button.click()

        self.assertEqual(self.driver.title, 'Welcome')
        
