from django.template import Context, Template

import pytest

from tests.factories import IssuerFactory, OrderFactory, PaymentOptionsFactory


@pytest.mark.django_db
def test_adyen_session_dropin_component_no_styles(
    settings,
    mock_sessions_api_success,
) -> None:
    """
    Test donation component with a valid campaign
    :param donation_campaign_example: Example Donation Campaign
    """

    settings.DJADYEN_STYLES = None
    order = OrderFactory.build()

    payment = PaymentOptionsFactory(adyen_name="schema", is_active=True)
    IssuerFactory(adyen_id="mc", name="MasterCard", payment_option=payment)
    IssuerFactory(adyen_id="visa", name="Visa", payment_option=payment)

    out = Template(
        "{% load adyen_tags %}"
        "{% adyen_session_dropin_component language=adyen_language order=order  %}"
    ).render(
        Context(
            {
                "adyen_language": "en-US",
                "order": order,
            }
        )
    )

    assert "adyen_id" in out
    assert "MasterCard" in out
