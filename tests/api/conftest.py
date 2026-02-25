import re

from django.urls import reverse

import pytest

from tests.factories import OrderFactory


@pytest.fixture
def payments_api() -> tuple[str, OrderFactory]:
    order = OrderFactory()
    payments_api_url = reverse("payments_api", args=[order.reference])
    return payments_api_url, order


@pytest.fixture
def mock_successful_payments_api(requests_mock):
    """
    Example Payments api response v71 base on the adyen docs:
    https://docs.adyen.com/api-explorer/Checkout/71/post/payments
    :param requests_mock:
    :return: requests_mock
    """

    matcher = re.compile(r"https://checkout-test\.adyen\.com/v[0-9]{2}/payments")

    success_response = {
        "additionalData": {
            "cvcResult": "1 Matches",
            "authCode": "065696",
            "avsResult": "4 AVS not supported for this card type",
            "avsResultRaw": "4",
            "cvcResultRaw": "M",
            "refusalReasonRaw": "AUTHORISED",
            "acquirerCode": "TestPmmAcquirer",
            "acquirerReference": "8PQMP9VIE9N",
        },
        "pspReference": "993617895215577D",
        "resultCode": "Authorised",
        "merchantReference": "string",
        # TODO: update with real example if added to docs
        "donationToken": "EXAMPLE_DONATION_TOKEN",
    }

    requests_mock.post(matcher, json=success_response)
    return requests_mock
