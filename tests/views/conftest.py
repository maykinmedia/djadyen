import re

from django.urls import reverse

import pytest

from tests.factories import OrderFactory, PaymentOptionsFactory


@pytest.fixture
def setup_advanced_view() -> tuple[str, OrderFactory]:
    order = OrderFactory()
    payments_api_url = reverse("advance_payment", args=[order.reference])
    return payments_api_url, order


@pytest.fixture
def setup_donation_view() -> tuple[str, OrderFactory]:
    order = OrderFactory(payment_option=PaymentOptionsFactory())
    payments_api_url = reverse("donation", args=[order.reference])
    return payments_api_url, order


@pytest.fixture
def mock_donation_campaign_api(requests_mock):
    """
    Example Donation Campaign api response v71 base on the adyen docs:
    https://docs.adyen.com/api-explorer/Checkout/71/post/donationCampaigns
    :param requests_mock:
    :return: requests_mock
    """

    matcher = re.compile(
        r"https://checkout-test\.adyen\.com/v[0-9]{2}/donationCampaigns"
    )

    success_response = {
        "donationCampaigns": [
            {
                "id": "DONATION_CAMPAIGN_ID",
                "campaignName": "DONATION_CAMPAIGN_NAME",
                "donation": {
                    "currency": "EUR",
                    "type": "fixedAmounts",
                    "donationType": "fixedAmounts",
                    "values": [100, 200, 300],
                },
                "nonprofitName": "NONPROFIT_NAME",
                "causeName": "NONPROFIT_CAUSE",
                "nonprofitDescription": "NONPROFIT_DESCRIPTION.",
                "nonprofitUrl": "NONPROFIT_WEBSITE_URL",
                "logoUrl": "NONPROFIT_LOGO_URL",
                "bannerUrl": "NONPROFIT_BANNER_URL",
                "termsAndConditionsUrl": "NONPROFIT_TERMS_AND_CONDITIONS_URL",
            },
            {
                "id": "DONATION_CAMPAIGN_ID",
                "campaignName": "DONATION_CAMPAIGN_NAME",
                "donation": {
                    "currency": "EUR",
                    "type": "roundup",
                    "donationType": "roundup",
                    "maxRoundupAmount": 100,
                },
                "nonprofitName": "NONPROFIT_NAME",
                "causeName": "NONPROFIT_CAUSE",
                "nonprofitDescription": "NONPROFIT_DESCRIPTION.",
                "nonprofitUrl": "NONPROFIT_WEBSITE_URL",
                "logoUrl": "NONPROFIT_LOGO_URL",
                "bannerUrl": "NONPROFIT_BANNER_URL",
                "termsAndConditionsUrl": "NONPROFIT_TERMS_AND_CONDITIONS_URL",
            },
        ]
    }

    requests_mock.post(matcher, json=success_response)
    return requests_mock


@pytest.fixture
def mock_donations_api(requests_mock):
    """
    Example Donations api response v71 base on the adyen docs:
    https://docs.adyen.com/api-explorer/Checkout/71/post/donations
    :param requests_mock:
    :return: requests_mock
    """

    matcher = re.compile(r"https://checkout-test\.adyen\.com/v[0-9]{2}/donations")

    success_response = {
        "id": "UNIQUE_RESOURCE_ID",
        "status": "completed",
        "merchantAccount": "YOUR_MERCHANT_ACCOUNT",
        "amount": {"currency": "EUR", "value": 1000},
        "reference": "YOUR_DONATION_REFERENCE",
        "payment": {
            "pspReference": "8535762347980628",
            "resultCode": "Authorised",
            "amount": {"currency": "EUR", "value": 1000},
            "merchantReference": "YOUR_DONATION_REFERENCE",
        },
    }

    requests_mock.post(matcher, json=success_response)
    return requests_mock


@pytest.fixture
def mock_donations_api_exception(requests_mock):
    """
    Example error Donations api response v71 base on the adyen docs:
    https://docs.adyen.com/api-explorer/Checkout/71/post/donations
    https://docs.adyen.com/development-resources/error-codes
    :param requests_mock:
    :return: requests_mock
    """

    matcher = re.compile(r"https://checkout-test\.adyen\.com/v[0-9]{2}/donations")

    bad_response = {
        "status": 400,
        "errorCode": "100",
        "message": "Required object 'amount' is not provided",
        "errorType": "validation",
        "pspReference": "F7WCWRG6JPHR8HG2",
    }

    requests_mock.post(matcher, json=bad_response, status_code=400)
    return requests_mock


@pytest.fixture
def mock_donations_api_refused(requests_mock):
    """
    Example Donations api response v71 base on the adyen docs:
    https://docs.adyen.com/api-explorer/Checkout/71/post/donations
    :param requests_mock:
    :return: requests_mock
    """

    matcher = re.compile(r"https://checkout-test\.adyen\.com/v[0-9]{2}/donations")

    success_response = {
        "id": "UNIQUE_RESOURCE_ID",
        "status": "refused",
        "merchantAccount": "YOUR_MERCHANT_ACCOUNT",
        "amount": {"currency": "EUR", "value": 1000},
        "reference": "YOUR_DONATION_REFERENCE",
        "payment": {
            "pspReference": "8535762347980628",
            "resultCode": "Error",
            "amount": {"currency": "EUR", "value": 1000},
            "merchantReference": "YOUR_DONATION_REFERENCE",
        },
    }

    requests_mock.post(matcher, json=success_response)
    return requests_mock
