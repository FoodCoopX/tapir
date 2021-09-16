import datetime

import django.utils.timezone
from django.test import tag
from django.urls import reverse

from tapir.shifts.models import ShiftTemplate
from tapir.utils.tests_utils import TapirSeleniumTestBase, TAPIR_SELENIUM_BASE_FIXTURES


class TestMemberSelfRegisterToShift(TapirSeleniumTestBase):
    fixtures = TAPIR_SELENIUM_BASE_FIXTURES + [
        "test_member_self_registers_to_shift.json",
    ]
    TEMPLATE_SHIFT_ID = 1000
    SHIFT_NAME = "SeleniumTestAbcdShift"

    @tag("selenium")
    def test_member_self_registers_to_flying_shift(self):
        shift = ShiftTemplate.objects.get(id=self.TEMPLATE_SHIFT_ID).create_shift(
            django.utils.timezone.now().date() + datetime.timedelta(days=1)
        )

        standard_user = self.get_standard_user()
        self.login(standard_user.get_username(), standard_user.get_username())
        self.selenium.get(self.live_server_url + reverse("shifts:upcoming_timetable"))
        self.wait_until_element_present_by_id("upcoming-shifts-timetable")
        self.selenium.find_element_by_id(f"shift_{shift.id}").click()
        self.wait_until_element_present_by_id("shift_detail_card")
        self.selenium.find_elements_by_class_name("register-self-button")[0].click()
        self.assertEqual(
            standard_user.first_name,
            self.selenium.find_element_by_class_name("shift-user").text,
        )
        self.selenium.get(self.live_server_url + reverse("accounts:user_me"))
        self.assertIn(
            self.SHIFT_NAME,
            self.selenium.find_element_by_id("upcoming_shift").text,
        )
