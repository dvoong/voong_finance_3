from functional_tests.TestCase import TestCase

class TestHomeRedirectsToLogin(TestCase):

    def test(self):

        self.driver.get(self.live_server_url + '/home')
        self.assertEqual(self.live_server_url + '/welcome?next=/home', self.driver.current_url)
