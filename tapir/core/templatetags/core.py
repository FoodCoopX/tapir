from django import template
from django.apps import apps
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from tapir.core.hooks import sidebar_link_groups_provider
from tapir.core.models import SidebarLinkGroup

register = template.Library()


@register.simple_tag
def is_app_installed(app):
    return apps.is_installed(app)


@register.inclusion_tag("core/sidebar_links.html", takes_context=True)
def sidebar_links(context):
    groups = []
    for provider in sidebar_link_groups_provider:
        groups += provider(context["request"])

    for group in groups:
        for link in group.links:
            link["is_active"] = link["url"] == context["request"].path

    context["sidebar_link_groups"] = groups

    return context


def get_org_link_groups(request):
    groups = []
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


sidebar_link_groups_provider.append(get_org_link_groups)
