from json import dumps

from django.template import Context, Template
from django.utils.html import escape

from djadyen.settings import get_setting
from tests.factories import OrderFactory


def test_adyen_advanced_payment_component_no_styles(settings) -> None:
    """
    Test donation component with a valid campaign
    :param donation_campaign_example: Example Donation Campaign
    """

    settings.DJADYEN_STYLES = None
    order = OrderFactory.build()

    out = Template(
        "{% load adyen_tags %}"
        "{% adyen_advanced_payment_component language=adyen_language order=order  %}"  # noqa
    ).render(
        Context(
            {
                "adyen_language": "en-US",
                "order": order,
            }
        )
    )

    assert "data-styles=" not in out
    assert get_setting("DJADYEN_DEFAULT_COUNTRY_CODE") in out


def test_adyen_advanced_payment_component_with_styles(settings) -> None:
    """
    Test donation component with a valid campaign
    :param donation_campaign_example: Example Donation Campaign
    """

    settings.DJADYEN_STYLES = {
        "base": {
            "color": "#000000",
            "fontSize": "16px",
            "fontFamily": "Arial, sans-serif",
        },
        "placeholder": {
            "color": "#999999",
        },
        "error": {
            "color": "#ff0000",
        },
    }

    order = OrderFactory.build()

    out = Template(
        "{% load adyen_tags %}"
        "{% adyen_advanced_payment_component language=adyen_language order=order  %}"  # noqa
    ).render(
        Context(
            {
                "adyen_language": "en-US",
                "order": order,
            }
        )
    )

    assert "data-styles=" in out
    assert escape(dumps(settings.DJADYEN_STYLES)) in out
    assert get_setting("DJADYEN_DEFAULT_COUNTRY_CODE") in out
