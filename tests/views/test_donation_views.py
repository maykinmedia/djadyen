from django.urls import reverse
from django.utils.translation import get_language

import pytest

from djadyen.choices import Status


@pytest.mark.django_db()
def test_donation_view_no_order(client):
    """
    Test that the donation view requires an order or 404s
    """
    advanced_url = reverse("donation", args=["00000000-0000-0000-0000-000000000000"])

    response = client.get(advanced_url)
    assert response.status_code == 404


@pytest.mark.django_db()
def test_donation_view_simple(client, setup_donation_view, mock_donation_campaign_api):
    """
    Test that the donation view renders correctly with a simple order
    """
    url, order = setup_donation_view
    response = client.get(url)

    assert response.status_code == 200
    assert type(response.context["campaign"]) is dict


@pytest.mark.django_db()
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


@pytest.mark.django_db()
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
