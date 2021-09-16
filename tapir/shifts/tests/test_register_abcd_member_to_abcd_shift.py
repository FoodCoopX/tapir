import datetime
import time

import django.utils.timezone
from django.test import tag

from tapir.accounts.models import TapirUser
from tapir.shifts.models import ShiftTemplate, ShiftAttendance, ShiftUserCapability
from tapir.utils.tests_utils import TapirSeleniumTestBase, TAPIR_SELENIUM_BASE_FIXTURES


class TestRegisterAbcdMemberToAbcdShift(TapirSeleniumTestBase):
    fixtures = TAPIR_SELENIUM_BASE_FIXTURES + [
        "test_register_abcd_member_to_abcd_shift.json",
    ]
    TEMPLATE_SHIFT_ID = 1000
    SHIFT_NAME = "SeleniumTestAbcdShift"

    # register a member to an ABCD shift and check that they get registered to the corresponding shift instance
    @tag("selenium")
    def test_register_abcd_member_to_abcd_shift(self):
        ShiftTemplate.objects.get(id=self.TEMPLATE_SHIFT_ID).create_shift(
            django.utils.timezone.now().date() + datetime.timedelta(days=1)
        )
        blocked_shift = ShiftTemplate.objects.get(
            id=self.TEMPLATE_SHIFT_ID
        ).create_shift(django.utils.timezone.now().date() + datetime.timedelta(days=2))
        ShiftAttendance.objects.create(
            slot=blocked_shift.slots.all()[0],
            user=TapirUser.objects.get(username="blocking.user"),
        )

        member_office_user = self.get_member_office_user()
        self.login(member_office_user.get_username(), member_office_user.get_username())
        abcd_user = self.get_test_user("hilla.waisanen")
        shift_user_data = abcd_user.get_tapir_user().shift_user_data
        shift_user_data.capabilities.append(ShiftUserCapability.SHIFT_COORDINATOR)
        shift_user_data.save()
        self.go_to_user_page(abcd_user.get_display_name())

        self.wait_until_element_present_by_id("tapir_user_detail_card")
        self.selenium.find_element_by_id("find_abcd_shift_button").click()
        self.wait_until_element_present_by_id("repeated-shift-overview-table")
        self.selenium.find_element_by_id(f"template_{self.TEMPLATE_SHIFT_ID}").click()
        self.wait_until_element_present_by_id("shift_detail_card")
        self.selenium.find_elements_by_class_name("abcd_shift_register_button")[
            0
        ].click()
        self.wait_until_element_present_by_id("shift_form_card")
        self.assertIn(
            blocked_shift.get_display_name(),
            self.selenium.find_element_by_id("occupied_shifts_list").text,
        )
        self.selenium.find_element_by_xpath('//button[@type="submit"]').click()

        self.go_to_user_page(abcd_user.get_display_name())
        self.assertIn(
            self.SHIFT_NAME,
            self.selenium.find_element_by_class_name("repeated-shift").text,
        )
        self.assertIn(
            self.SHIFT_NAME,
            self.selenium.find_element_by_id("upcoming_shift").text,
        )
