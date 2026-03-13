import re

import pytest


@pytest.fixture
def mock_redirect_ideal_payments_api(requests_mock):
    """
    Example Payments api response v71 base on the adyen docs:
    https://docs.adyen.com/api-explorer/Checkout/71/post/payments
    :param requests_mock:
    :return: requests_mock
    """

    matcher = re.compile(r"https://checkout-test\.adyen\.com/v[0-9]{2}/payments")

    success_response = {
        "resultCode": "RedirectShopper",
        "action": {
            "paymentMethodType": "ideal",
            "url": "https://test.adyen.com/hpp/checkout.shtml",
            "method": "GET",
            "type": "redirect",
        },
    }

    requests_mock.post(matcher, json=success_response)
    return requests_mock
