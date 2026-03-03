import pytest


@pytest.fixture
def donation_campaign_example() -> dict:
    """
    Example Donation Campaign take from v71 base on the adyen docs:
    https://docs.adyen.com/api-explorer/Checkout/71/post/donationCampaigns
    :return: requests_mock
    """

    return {
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
    }
