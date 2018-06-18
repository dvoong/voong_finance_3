from django.core import mail
from functional_tests.welcome.WelcomePage import RegistrationForm, LoginForm
from functional_tests.homepage.HomePage import HomePage
from functional_tests.TestCase import TestCase

class TestRegistration(TestCase):

    def get_registration_link_from_email(self, email):
        body = email.body
        url = '{}/activate'.format(self.live_server_url)
        filtered_rows = list(filter(lambda x: x.startswith(url), body.split('\n')))
        assert len(filtered_rows) == 1, filtered_rows
        return filtered_rows[0]

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

        self.assertEqual(self.driver.current_url, '{}/verify-email'.format(self.live_server_url))
        self.assertEqual(len(mail.outbox), 1, mail.outbox)
        email = mail.outbox[0]
        self.assertEqual(email.recipients(), ['voong.david@gmail.com'])
        self.assertEqual(email.subject, 'Verify your email')
        self.assertEqual(email.from_email, 'registration@voong-finance.co.uk')

        # user clicks on registration link
        registration_link = self.get_registration_link_from_email(email)
        self.driver.get(registration_link)

        self.assertEqual(self.driver.current_url, '{}/home'.format(self.live_server_url))
        

    
