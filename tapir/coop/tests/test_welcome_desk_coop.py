from django.urls import reverse

from tapir.accounts.models import TapirUser
from tapir.coop.models import ShareOwner
from tapir.coop.tests.factories import ShareOwnerFactory
from tapir.utils.tests_utils import TapirFactoryTestBase


class TestWelcomeDeskBase(TapirFactoryTestBase):
    class Messages:
        CAN_SHOP = "welcome_desk_can_shop"
        NO_ACCOUNT = "welcome_desk_no_account"
        SHIFT_BALANCE_NOT_OK = "welcome_desk_shift_balance_not_ok"
        IS_INVESTING = "welcome_desk_is_investing"
        NO_ABCD_SHIFT = "welcome_desk_no_abcd_shift"
        NO_WELCOME_SESSION = "welcome_desk_no_welcome_session"

    MESSAGES = [
        Messages.CAN_SHOP,
        Messages.NO_ACCOUNT,
        Messages.SHIFT_BALANCE_NOT_OK,
        Messages.IS_INVESTING,
        Messages.NO_ABCD_SHIFT,
        Messages.NO_WELCOME_SESSION,
    ]

    @staticmethod
    def get_no_warnings_user() -> TapirUser:
        return TapirFactoryTestBase.get_tapir_user_factory().create(
            share_owner__is_investing=False, share_owner__attended_welcome_session=True
        )

    def check_alerts(self, share_owner: ShareOwner, expected_messages):
        self.login_as_member_office_user()
        response = self.client.get(
            reverse("coop:welcome_desk_share_owner", args=[share_owner.id])
        )
        response_content = response.content.decode()
        for message in self.MESSAGES:
            if message in expected_messages:
                self.assertIn(
                    message,
                    response_content,
                    f"Message {message} should be showing for user {share_owner.get_info().get_display_name()}",
                )
            else:
                self.assertNotIn(
                    message,
                    response_content,
                    f"Message {message} should not be showing for user {share_owner.get_info().get_display_name()}",
                )


class TestWelcomeDeskCoop(TestWelcomeDeskBase):
    def test_member_office_user(self):
        self.login_as_member_office_user()
        response = self.client.get(reverse("accounts:user_me"), follow=True)

        self.assertTrue(
            response.context["request"].user.has_perm("welcomedesk.view"),
            "Member office users should always have access to the welcome desk.",
        )
        self.assertIn(
            "welcome_desk_link",
            response.content.decode(),
            "The user should have access to the welcome desk page, therefore the link should be visible.",
        )

    def test_no_warnings(self):
        self.check_alerts(
            self.get_no_warnings_user().share_owner, [self.Messages.CAN_SHOP]
        )

    def test_no_account(self):
        self.check_alerts(
            ShareOwnerFactory.create(attended_welcome_session=True, is_investing=False),
            [self.Messages.NO_ACCOUNT],
        )

    def test_is_investing(self):
        user = self.get_no_warnings_user()
        user.share_owner.is_investing = True
        user.share_owner.save()
        self.check_alerts(user.share_owner, [self.Messages.IS_INVESTING])

    def test_no_welcome_session(self):
        user = self.get_no_warnings_user()
        user.share_owner.attended_welcome_session = False
        user.share_owner.save()
        self.check_alerts(
            user.share_owner, [self.Messages.NO_WELCOME_SESSION, self.Messages.CAN_SHOP]
        )
