from django.http import QueryDict
from django.urls import reverse

from tapir.coop.tests.test_share_owner_list_filters_coop import TestShareOwnerListBase
from tapir.shifts.models import (
    ShiftTemplateGroup,
    ShiftSlotTemplate,
    ShiftAttendanceTemplate,
    ShiftUserCapability,
)
from tapir.shifts.tests.factories import ShiftTemplateFactory


class TestShareOwnerListCoop(TestShareOwnerListBase):
    def test_abcd_week(self):
        for name in ["A", "B"]:
            ShiftTemplateGroup.objects.create(name=name)

        group = ShiftTemplateGroup.objects.get(name="A")
        owners_in_group = []
        for _ in range(2):
            shift_template = ShiftTemplateFactory.create(group=group)
            user = self.get_tapir_user_factory().create()
            owners_in_group.append(user.share_owner)
            ShiftAttendanceTemplate.objects.create(
                user=user,
                slot_template=ShiftSlotTemplate.objects.get(
                    shift_template=shift_template
                ),
            )

        owners_not_in_group = []
        for i in range(2):
            shift_template = ShiftTemplateFactory.create(
                group=None if i == 0 else ShiftTemplateGroup.objects.get(name="B")
            )
            user = self.get_tapir_user_factory().create()
            owners_not_in_group.append(user.share_owner)
            ShiftAttendanceTemplate.objects.create(
                user=user,
                slot_template=ShiftSlotTemplate.objects.get(
                    shift_template=shift_template
                ),
            )

        self.visit_view(
            {"abcd_week": "A"},
            must_be_in=owners_in_group,
            must_be_out=owners_not_in_group,
        )

    def test_has_qualification(self):
        owners_with_capability = [
            self.get_tapir_user_factory()
            .create(shift_capabilities=[ShiftUserCapability.SHIFT_COORDINATOR])
            .share_owner
            for _ in range(2)
        ]

        owners_without_capability = [
            self.get_tapir_user_factory()
            .create(shift_capabilities=[ShiftUserCapability.CASHIER])
            .share_owner,
            self.get_tapir_user_factory().create(shift_capabilities=[]).share_owner,
        ]

        self.visit_view(
            {"has_capability": ShiftUserCapability.SHIFT_COORDINATOR},
            must_be_in=owners_with_capability,
            must_be_out=owners_without_capability,
        )

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
