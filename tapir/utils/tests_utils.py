import socket

import factory.random
from django.apps import apps
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.db import DEFAULT_DB_ALIAS
from django.test import TestCase, override_settings, Client
from django.urls import reverse
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

import tapir
from tapir.accounts.models import TapirUser
from tapir.accounts.templatetags.accounts import format_phone_number
from tapir.accounts.tests.factories.factories import TapirUserFactory
from tapir.utils.json_user import JsonUser


class LdapEnabledTestCase(TestCase):
    databases = {"ldap", DEFAULT_DB_ALIAS}


@override_settings(ALLOWED_HOSTS=["*"])
class TapirSeleniumTestBase(LdapEnabledTestCase, StaticLiveServerTestCase):
    DEFAULT_TIMEOUT = 5
    selenium: WebDriver
    host = "0.0.0.0"  # Bind to 0.0.0.0 to allow external access

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.host = socket.gethostbyname(socket.gethostname())
        cls.selenium = webdriver.Remote(
            command_executor=f"http://selenium:4444/wd/hub",
            desired_capabilities=DesiredCapabilities.FIREFOX,
        )
        cls.selenium.maximize_window()
        cls.selenium.implicitly_wait(cls.DEFAULT_TIMEOUT)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self) -> None:
        super().setUp()
        factory.random.reseed_random(self.__class__.__name__)

    def login(self, username: str, password: str):
        self.selenium.get(self.live_server_url + reverse("login"))
        login_card = self.selenium.find_element_by_id("login-card")
        login_card.find_element_by_id("id_username").send_keys(username)
        login_card.find_element_by_id("id_password").send_keys(password)
        login_card.find_element_by_tag_name("button").click()
        self.wait_until_element_present_by_id("logout")

    def logout_if_necessary(self):
        url_before = self.selenium.current_url

        if not self.does_element_exist_by_id("logout"):
            return
        logout_button = self.selenium.find_element_by_id("logout")
        logout_button.click()
        self.wait_until_element_present_by_id("login-card")

        self.selenium.get(url_before)

    def does_element_exist_by_id(self, html_id: str) -> bool:
        try:
            self.selenium.implicitly_wait(1)
            self.selenium.find_element_by_id(html_id)
        except NoSuchElementException:
            return False
        finally:
            self.selenium.implicitly_wait(self.DEFAULT_TIMEOUT)

        return True

    def does_element_exist_by_class_name(self, class_name: str) -> bool:
        return len(self.selenium.find_elements_by_class_name(class_name)) > 0

    def wait_until_element_present_by_id(self, html_id: str):
        try:
            WebDriverWait(self.selenium, self.DEFAULT_TIMEOUT).until(
                ec.presence_of_element_located((By.ID, html_id))
            )
        except TimeoutException:
            self.fail("Missing element with ID " + html_id)

    def wait_until_element_present_by_class_name(self, html_class: str):
        try:
            WebDriverWait(self.selenium, self.DEFAULT_TIMEOUT).until(
                ec.presence_of_element_located((By.CLASS_NAME, html_class))
            )
        except TimeoutException:
            self.fail("Missing element with class " + html_class)


class TapirUserTestBase(TapirSeleniumTestBase):
    def check_tapir_user_details(self, user: JsonUser):
        self.assertEqual(
            self.selenium.find_element_by_id("tapir_user_display_name").text,
            user.get_display_name(),
        )
        self.assertEqual(
            self.selenium.find_element_by_id("tapir_user_username").text,
            user.get_username(),
        )
        self.assertEqual(
            self.selenium.find_element_by_id("tapir_user_email").text,
            user.email,
        )
        self.assertEqual(
            self.selenium.find_element_by_id("tapir_user_phone_number").text,
            format_phone_number(user.phone_number),
        )
        self.assertEqual(
            self.selenium.find_element_by_id("tapir_user_birthdate").text,
            user.get_birthdate_display(),
        )
        self.assertEqual(
            self.selenium.find_element_by_id("tapir_user_address").text,
            user.get_display_address(),
        )
        self.assertEqual(
            self.selenium.find_element_by_id("share_owner_status").text,
            "Active",
        )
        self.assertEqual(
            self.selenium.find_element_by_id("share_owner_num_shares").text,
            str(user.num_shares),
        )


class TapirFactoryTestBase(LdapEnabledTestCase):
    client: Client

    def setUp(self) -> None:
        super().setUp()
        factory.random.reseed_random(self.__class__.__name__)
        self.client = Client()

    def login_as_user(self, user: TapirUser):
        success = self.client.login(username=user.username, password=user.username)
        self.assertTrue(success, f"User {user.username} should be able to log in.")

    def login_as_member_office_user(self) -> TapirUser:
        user = self.get_tapir_user_factory().create(is_in_member_office=True)
        self.login_as_user(user)
        return user

    def login_as_normal_user(self) -> TapirUser:
        user = self.get_tapir_user_factory().create(is_in_member_office=False)
        self.login_as_user(user)
        return user

    @staticmethod
    def get_tapir_user_factory():
        mixins = [TapirUserFactory]
        if apps.is_installed("tapir.shifts"):
            mixins.append(tapir.shifts.tests.factories.TapirUserWithShiftsFactoryMixin)

        return type("CustomTapirUserFactory", tuple(mixins), {})
