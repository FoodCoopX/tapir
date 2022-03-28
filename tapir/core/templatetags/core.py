from django import template
from django.apps import apps
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

import tapir
from tapir.coop.models import FinancingCampaign
from tapir.core.models import SidebarLinkGroup

register = template.Library()


@register.simple_tag
def is_app_installed(app):
    return apps.is_installed(app)


@register.inclusion_tag("core/sidebar_links.html", takes_context=True)
def sidebar_links(context):
    groups = get_sidebar_link_groups(context["request"])

    for group in groups:
        for link in group.links:
            link["is_active"] = link["url"] == context["request"].path

    context["sidebar_link_groups"] = groups

    return context


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

    if apps.is_installed("tapir.shifts"):
        groups += tapir.shifts.templatetags.shifts.get_sidebar_link_groups(request)

    if FinancingCampaign.objects.exists():
        campaign_group = SidebarLinkGroup(name=_("Financing campaign"))
        groups.append(campaign_group)
        for campaign in FinancingCampaign.objects.all():
            campaign_group.add_link(
                display_name=_(campaign.name),
                material_icon="euro",
                url=campaign.get_absolute_url(),
            )

    misc_group = SidebarLinkGroup(name=_("Miscellaneous"))
    groups.append(misc_group)
    misc_group.add_link(
        display_name=_("Wiki"),
        material_icon="feed",
        url="https://wiki.supercoop.de",
    )
    misc_group.add_link(
        display_name=_("Member manual"),
        material_icon="menu_book",
        url="https://wiki.supercoop.de/wiki/Member_Manual",
    )
    misc_group.add_link(
        display_name=_("Shop opening hours"),
        material_icon="access_time",
        url="https://wiki.supercoop.de/wiki/%C3%96ffnungszeiten",
    )
    misc_group.add_link(
        display_name=_("Contact the member office"),
        material_icon="email",
        url="mailto:mitglied@supercoop.de",
    )
    misc_group.add_link(
        display_name=_("About tapir"),
        material_icon="help",
        url=reverse_lazy("coop:about"),
    )

    return groups
