from json import dumps

from django.template import Context, Template
from django.utils.html import escape
from django.utils.translation import gettext as _

from djadyen.settings import get_setting


def test_adyen_donation_component_no_campaign() -> None:
    """
    Test donation component with no campaign.
    The component should not be displayed and a message should shown instead
    """

    redirect_url = "https://www.example.com/donation/complete/"

    out = Template(
        "{% load adyen_tags %}"
        "{% adyen_donation_component language=adyen_language campaign=campaign redirect_url=redirect_url %}"  # noqa
    ).render(
        Context(
            {"adyen_language": "en-US", "campaign": None, "redirect_url": redirect_url}
        )
    )

    assert f"<p>{_('No active donation campaigns.')}</p>" in out


def test_adyen_donation_component(donation_campaign_example) -> None:
    """
    Test donation component with a valid campaign
    :param donation_campaign_example: Example Donation Campaign
    """
    redirect_url = "https://www.example.com/donation/complete/"

    out = Template(
        "{% load adyen_tags %}"
        "{% adyen_donation_component language=adyen_language campaign=campaign redirect_url=redirect_url %}"  # noqa
    ).render(
        Context(
            {
                "adyen_language": "en-US",
                "campaign": donation_campaign_example,
                "redirect_url": redirect_url,
            }
        )
    )

    assert escape(dumps(donation_campaign_example)) in out
    assert get_setting("DJADYEN_DEFAULT_COUNTRY_CODE") in out
