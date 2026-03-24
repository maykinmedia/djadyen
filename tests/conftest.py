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


@pytest.fixture
def mock_refused_payment_details_api(requests_mock):
    """
    Example Payment Details api refused response v71 based on the adyen docs:
    https://docs.adyen.com/api-explorer/Checkout/71/post/payments/details
    :param requests_mock:
    :return: requests_mock
    """

    matcher = re.compile(
        r"https://checkout-test\.adyen\.com/v[0-9]{2}/payments/details"
    )
    # TODO: update with real /payment/details/ example
    success_response = {
        "pspReference": "PSP_EXAMPLE_IDEAL",
        "resultCode": "Refused",
        "amount": {"currency": "EUR", "value": 400},
        "merchantReference": "string",
        "paymentMethod": {"type": "ideal"},
    }

    requests_mock.post(matcher, json=success_response)
    return requests_mock


@pytest.fixture
def mock_successful_payment_details_api(requests_mock):
    """
    Example Payment Details api response v71 base on the adyen docs:
    https://docs.adyen.com/api-explorer/Checkout/71/post/payments/details
    :param requests_mock:
    :return: requests_mock
    """

    matcher = re.compile(
        r"https://checkout-test\.adyen\.com/v[0-9]{2}/payments/details"
    )
    success_response = {
        "pspReference": "PSP_EXAMPLE_IDEAL",
        "resultCode": "Authorised",
        "amount": {"currency": "EUR", "value": 400},
        "donationToken": "DONATION_IDEAL_TOKEN",
        "merchantReference": "string",
        "paymentMethod": {"type": "ideal"},
    }

    requests_mock.post(matcher, json=success_response)
    return requests_mock
