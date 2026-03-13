import re

from django.urls import reverse

import pytest

from tests.factories import OrderFactory


@pytest.fixture
def setup_payments_api() -> tuple[str, OrderFactory]:
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
def mock_payments_api_exception(requests_mock):
    """
    Example Payments api 500 response v71 base on the adyen docs
    copied from failed /payments/ api:
    https://docs.adyen.com/api-explorer/Checkout/71/post/payments
    https://docs.adyen.com/development-resources/error-codes
    :param requests_mock:
    :return: requests_mock
    """

    matcher = re.compile(r"https://checkout-test\.adyen\.com/v[0-9]{2}/payments")

    bad_response = {
        "status": 500,
        "errorCode": "905_1",
        "message": "Could not find an acquirer account for the provided txvariant "
        "(alipay), currency (EUR), and action (AUTH).",
        "errorType": "configuration",
        "pspReference": "PSP_EXAMPLE",
    }

    requests_mock.post(
        matcher,
        json=bad_response,
        status_code=500,
        headers={"pspReference": "PSP_EXAMPLE"},
    )
    return requests_mock


@pytest.fixture
def setup_payment_details_api() -> tuple[str, OrderFactory]:
    order = OrderFactory()
    payments_api_url = reverse("payment_details_api", args=[order.reference])
    return payments_api_url, order


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
        "resultCode": "Authorised",
        "pspReference": "V4HZ4RBFJGXXGN82",
        # TODO: update with real example if added to docs
        "donationToken": "EXAMPLE_DONATION_TOKEN",
    }

    requests_mock.post(matcher, json=success_response)
    return requests_mock


@pytest.fixture
def mock_payment_details_api_exception(requests_mock):
    """
    Example Payments Details api 500 response v71 base on the adyen docs
    copied from failed /payments/ api:
    https://docs.adyen.com/api-explorer/Checkout/71/post/payments/details
    https://docs.adyen.com/development-resources/error-codes
    :param requests_mock:
    :return: requests_mock
    """

    matcher = re.compile(
        r"https://checkout-test\.adyen\.com/v[0-9]{2}/payments/details"
    )

    # TODO: update with real /payment/details/ example instead of /payments/
    bad_response = {
        "status": 500,
        "errorCode": "905_1",
        "message": "Could not find an acquirer account for the provided txvariant "
        "(alipay), currency (EUR), and action (AUTH).",
        "errorType": "configuration",
        "pspReference": "PSP_EXAMPLE",
    }

    requests_mock.post(
        matcher,
        json=bad_response,
        status_code=500,
        headers={"pspReference": "PSP_EXAMPLE"},
    )
    return requests_mock
