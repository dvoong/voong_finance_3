import time
from selenium.webdriver import Chrome
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

class Test(StaticLiveServerTestCase):

    def setUp(self):
        self.driver = Chrome()

    def test(self):
        self.driver.get(self.live_server_url)
        self.assertEqual(self.driver.title, 'Welcome')

