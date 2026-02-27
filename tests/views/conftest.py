import re

from django.urls import reverse

import pytest

from tests.factories import OrderFactory


@pytest.fixture
def setup_advanced_view() -> tuple[str, OrderFactory]:
    order = OrderFactory()
    payments_api_url = reverse("advance_payment", args=[order.reference])
    return payments_api_url, order


@pytest.fixture
def setup_donation_view() -> tuple[str, OrderFactory]:
    order = OrderFactory()
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
