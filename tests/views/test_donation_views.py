from json import dumps

from django.urls import reverse
from django.utils.translation import get_language

import pytest

from djadyen.choices import Status
from tests.factories import DonationFactory

pytestmark = [
    pytest.mark.django_db,
]


def test_donation_view_no_order(client):
    """
    Test that the donation view requires an order or 404s
    """
    advanced_url = reverse("donation", args=["00000000-0000-0000-0000-000000000000"])

    response = client.get(advanced_url)
    assert response.status_code == 404


def test_donation_view_simple(client, setup_donation_view, mock_donation_campaign_api):
    """
    Test that the donation view renders correctly with a simple order
    """
    url, order = setup_donation_view
    response = client.get(url)

    assert response.status_code == 200
    assert type(response.context["campaign"]) is dict


def test_donation_view_free_price(
    client, setup_donation_view, mock_donation_campaign_api
):
    """
    Test that the donation view renders correctly with a simple order
    """
    url, order = setup_donation_view
    order.amount = 0
    order.save()
    assert order.status == Status.Created

    response = client.get(url)

    order.refresh_from_db()
    assert response.status_code == 200
    assert order.status == Status.Authorised


def test_donation_view_language_code(
    client, setup_donation_view, mock_donation_campaign_api
):
    """
    Test that the adyen locale is used if get_locale is overridden
    """
    url, order = setup_donation_view

    response = client.get(url)

    assert get_language() == "en"
    assert response.context["adyen_language"] == "en-US"


def test_donation_view_creation_donation(
    client, setup_donation_view, mock_donations_api
):
    """
    Test normal donation creation
    """
    url, order = setup_donation_view

    response = client.post(
        url,
        {
            "amount": dumps({"value": "1000", "current": "EUR"}),
            "donation_campaign_id": "DONATION_CAMPAIGN_ID",
        },
    )
    assert response.status_code == 302

    order.refresh_from_db()
    assert order.donation_order.campaign == "DONATION_CAMPAIGN_ID"
    assert order.donation_order.amount == 1000
    assert order.donation_order.status == Status.Pending


def test_donation_view_creation_donation_exception(
    client, setup_donation_view, mock_donations_api_exception
):
    """
    Test Adyen api returning exception, as of Adyen python version 14.0.0
    """
    url, order = setup_donation_view

    response = client.post(
        url,
        {
            "amount": dumps({"value": "1000", "current": "EUR"}),
            "donation_campaign_id": "DONATION_CAMPAIGN_ID",
        },
    )
    assert response.status_code == 302

    order.refresh_from_db()
    assert order.donation_order.campaign == "DONATION_CAMPAIGN_ID"
    assert order.donation_order.amount == 1000
    assert order.donation_order.status == Status.Error


def test_donation_view_creation_donation_refused(
    client, setup_donation_view, mock_donations_api_refused
):
    """
    Test Adyen api returning refused donation response
    """
    url, order = setup_donation_view

    response = client.post(
        url,
        {
            "amount": dumps({"value": "1000", "current": "EUR"}),
            "donation_campaign_id": "DONATION_CAMPAIGN_ID",
        },
    )
    assert response.status_code == 302

    order.refresh_from_db()
    assert order.donation_order.campaign == "DONATION_CAMPAIGN_ID"
    assert order.donation_order.amount == 1000
    assert order.donation_order.status == Status.Refused


def test_donation_view_existing_pending_donation(client, setup_donation_view):
    """
    Test Adyen api returning with existing pending or started donation.
    It should not create use another API requestion and update campaign or amount
    """

    url, order = setup_donation_view

    donation = DonationFactory(
        order=order,
        status=Status.Pending,
        amount=1245,
        campaign="DIFFERENT_CAMPAIGN_ID",
    )

    response = client.post(
        url,
        {
            "amount": dumps({"value": "1000", "current": "EUR"}),
            "donation_campaign_id": "DONATION_CAMPAIGN_ID",
        },
    )
    assert response.status_code == 302

    donation.refresh_from_db()
    assert donation.status == Status.Pending
    assert donation.amount == 1245
    assert donation.campaign == "DIFFERENT_CAMPAIGN_ID"


def test_donation_view_existing_created_donation(
    client, setup_donation_view, mock_donations_api
):
    """
    Test Adyen api returning with existing created or non-run donation.
    The new donation should override the old one
    """

    url, order = setup_donation_view

    donation = DonationFactory(
        order=order,
        status=Status.Created,
        amount=1245,
        campaign="DIFFERENT_CAMPAIGN_ID",
    )

    response = client.post(
        url,
        {
            "amount": dumps({"value": "1000", "current": "EUR"}),
            "donation_campaign_id": "DONATION_CAMPAIGN_ID",
        },
    )
    assert response.status_code == 302

    donation.refresh_from_db()
    assert donation.status == Status.Pending
    assert donation.amount == 1000
    assert donation.campaign == "DONATION_CAMPAIGN_ID"
