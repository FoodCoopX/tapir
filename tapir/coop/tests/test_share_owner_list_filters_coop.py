import datetime

from django.http import QueryDict
from django.urls import reverse
from django.utils import timezone

from tapir.coop.models import ShareOwnership, COOP_SHARE_PRICE, MemberStatus
from tapir.coop.tests.factories import ShareOwnerFactory
from tapir.utils.tests_utils import TapirFactoryTestBase


class TestShareOwnerListBase(TapirFactoryTestBase):
    def visit_view(self, params: dict, must_be_in, must_be_out):
        self.login_as_member_office_user()

        query_dictionary = QueryDict("", mutable=True)
        query_dictionary.update(params)
        url = "{base_url}?{querystring}".format(
            base_url=reverse("coop:shareowner_list"),
            querystring=query_dictionary.urlencode(),
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        for owner in must_be_in:
            self.assertIn(
                owner,
                response.context["table"].rows.data,
                f"{owner.get_display_name()} should show up in the list filtered by {query_dictionary.urlencode()}.",
            )
        for owner in must_be_out:
            self.assertNotIn(
                owner,
                response.context["table"].rows.data,
                f"{owner.get_display_name()} should not show up in the list filtered by {query_dictionary.urlencode()}.",
            )
        return response


class TestShareOwnerListCoop(TestShareOwnerListBase):
    def test_requires_permissions(self):
        self.login_as_normal_user()

        response = self.client.get(reverse("coop:shareowner_list"))
        self.assertEqual(
            response.status_code,
            403,
            "Normal users should not have access to the member's list",
        )

    def test_has_unpaid_shares(self):
        # We must create several members, because if the filters only give one result back
        # we get redirected to the user's page directly
        owners_with_unpaid_share = []
        for _ in range(2):
            owner = ShareOwnerFactory.create()
            owners_with_unpaid_share.append(owner)
            shares = ShareOwnership.objects.filter(owner=owner)
            for share in shares:
                share.amount_paid = 0 if share == shares.first() else COOP_SHARE_PRICE
                share.save()

        owners_with_all_paid_share = []
        for _ in range(2):
            owner = ShareOwnerFactory.create()
            owners_with_all_paid_share.append(owner)
            for share in ShareOwnership.objects.filter(owner=owner):
                share.amount_paid = COOP_SHARE_PRICE
                share.save()

        self.visit_view(
            {"has_unpaid_shares": True},
            must_be_in=owners_with_unpaid_share,
            must_be_out=owners_with_all_paid_share,
        )
        self.visit_view(
            {"has_unpaid_shares": False},
            must_be_in=owners_with_all_paid_share,
            must_be_out=owners_with_unpaid_share,
        )

    def test_has_status(self):
        owners_with_status_sold = [
            ShareOwnerFactory.create(),
            self.get_tapir_user_factory().create().share_owner,
        ]
        for share_ownership in ShareOwnership.objects.filter(
            owner__in=owners_with_status_sold
        ):
            share_ownership.end_date = timezone.now() - datetime.timedelta(days=1)
            share_ownership.save()

        owners_with_status_investing = [
            ShareOwnerFactory.create(),
            self.get_tapir_user_factory().create().share_owner,
        ]
        for owner in owners_with_status_investing:
            owner.is_investing = True
            owner.save()

        owners_with_status_active = [
            ShareOwnerFactory.create(),
            self.get_tapir_user_factory().create().share_owner,
        ]
        for owner in owners_with_status_active:
            owner.is_investing = False
            owner.save()

        self.visit_view(
            {"status": MemberStatus.SOLD},
            must_be_in=owners_with_status_sold,
            must_be_out=owners_with_status_investing + owners_with_status_active,
        )

        self.visit_view(
            {"status": MemberStatus.ACTIVE},
            must_be_in=owners_with_status_active,
            must_be_out=owners_with_status_investing + owners_with_status_sold,
        )

        self.visit_view(
            {"status": MemberStatus.INVESTING},
            must_be_in=owners_with_status_investing,
            must_be_out=owners_with_status_active + owners_with_status_sold,
        )

    def test_attended_welcome_session(self):
        owners_who_attended = [
            ShareOwnerFactory.create(attended_welcome_session=True) for _ in range(2)
        ]
        owners_who_did_not_attend = [
            ShareOwnerFactory.create(attended_welcome_session=False) for _ in range(2)
        ]
        self.visit_view(
            {"attended_welcome_session": True},
            must_be_in=owners_who_attended,
            must_be_out=owners_who_did_not_attend,
        )
