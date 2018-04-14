from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from selenium.webdriver import Chrome
from functional_tests.welcome.WelcomePage import WelcomePage

class TestCase(StaticLiveServerTestCase):

    def setUp(self):
        self.driver = Chrome()

    def tearDown(self):
        self.driver.close()
        
    # def tearDown(self):
    #     if hasattr(self, '_outcome'):  # Python 3.4+
    #         result = self.defaultTestResult()  # these 2 methods have no side effects
    #         self._feedErrorsToResult(result, self._outcome.errors)
    #     else:  # Python 3.2 - 3.3 or 3.0 - 3.1 and 2.7
    #         result = getattr(self, '_outcomeForDoCleanups', self._resultForDoCleanups)
    #     error = self.list2reason(result.errors)
    #     failure = self.list2reason(result.failures)
    #     ok = not error and not failure

    #     # demo:   report short info immediately (not important)
    #     if not ok:
    #         import time
    #         # time.sleep(30)
    #         pass

    #     super().tearDown()

    def list2reason(self, exc_list):
        if exc_list and exc_list[-1][0] is self:
            return exc_list[-1][1]

    def create_user(self, email, password):
        User.objects.create_user(username=email, email=email, password=password)        

    def sign_in(self, email, password):
        url = '{}{}'.format(self.live_server_url, WelcomePage.url)
        self.driver.get(url)
        welcome_page = WelcomePage(self.driver)
        welcome_page.login_user(email, password)
