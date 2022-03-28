from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from tapir.coop.models import FinancingCampaign
from tapir.core.hooks import sidebar_link_groups_provider
from tapir.core.models import SidebarLinkGroup


def get_sidebar_link_groups(request):
    groups = []
    if request.user.has_perm("coop.manage"):
        coop_group = SidebarLinkGroup(name=_("Cooperative"))
        coop_group.add_link(
            display_name=_("Applicants"),
            material_icon="person_outline",
            url=reverse_lazy("coop:draftuser_list"),
        )
        coop_group.add_link(
            display_name=_("Members"),
            material_icon="person",
            url=reverse_lazy("coop:shareowner_list"),
        )
        coop_group.add_link(
            display_name=_("Matching program"),
            material_icon="card_giftcard",
            url=reverse_lazy("coop:matching_program_list"),
        )
        coop_group.add_link(
            display_name=_("Statistics"),
            material_icon="calculate",
            url=reverse_lazy("coop:statistics"),
        )
        groups.append(coop_group)

    if request.user.has_perm("welcomedesk.view"):
        welcomedesk_group = SidebarLinkGroup(name=_("Welcome Desk"))
        welcomedesk_group.add_link(
            display_name=_("Welcome Desk"),
            material_icon="table_restaurant",
            url=reverse_lazy("coop:welcome_desk_search"),
            html_id="welcome_desk_link",
        )
        groups.append(welcomedesk_group)

    if FinancingCampaign.objects.exists():
        campaign_group = SidebarLinkGroup(name=_("Financing campaign"))
        groups.append(campaign_group)
        for campaign in FinancingCampaign.objects.all():
            campaign_group.add_link(
                display_name=_(campaign.name),
                material_icon="euro",
                url=campaign.get_absolute_url(),
            )

    return groups


sidebar_link_groups_provider.append(get_sidebar_link_groups)
