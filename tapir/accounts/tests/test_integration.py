from django.test import tag

from tapir.utils.tests_utils import TapirSeleniumTestBase, TapirFactoryTestBase


class AccountsIntegrationTests(TapirSeleniumTestBase):
    @tag("selenium")
    def test_login_as_admin(self):
        self.selenium.get(self.live_server_url)
        self.logout_if_necessary()
        user = TapirFactoryTestBase.get_tapir_user_factory().create()
        self.login(user.username, user.username)
        self.assertIsNotNone(self.selenium.find_element_by_id("logout"))

    @tag("selenium")
    def test_redirect_to_login_page(self):
        self.selenium.get(self.live_server_url)
        self.logout_if_necessary()
        self.selenium.get(f"{self.live_server_url}/coop/member/")
        url = str(self.selenium.current_url)
        self.assertTrue("/accounts/login/" in url)
