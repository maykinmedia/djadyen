from django.urls import reverse

import pytest

from djadyen.choices import Status
from testapp.models import Donation, Order

EXPECTED_Updated_STATUS = [
    (Status.Authorised.value, True),
    (Status.Cancel.value, True),
    (Status.Created.value, False),
    (Status.Error.value, True),
    (Status.Pending.value, False),
    (Status.Refused.value, True),
]


@pytest.mark.django_db()
def test_order_status_view_no_order(client):
    """
    Test that the order status view requires an order or 404s
    """
    order_status_url = reverse(
        "order-status", args=["00000000-0000-0000-0000-000000000000"]
    )

    response = client.get(order_status_url)
    assert response.status_code == 404


@pytest.mark.django_db()
@pytest.mark.parametrize("status,updated_status", EXPECTED_Updated_STATUS)
def test_order_status_view(client, setup_order_status_view, status, updated_status):
    """
    Test that the order status views response is correct for status
    """
    order_status_url, order = setup_order_status_view
    order.status = status
    order.save()

    assert type(order) is Order

    response = client.get(order_status_url)
    assert response.status_code == 200

    assert response.json() == {
        "updatedStatus": updated_status,
        "currentStatus": status,
        "reference": str(order.reference),
    }


@pytest.mark.django_db()
def test_donation_status_view_no_donation(client):
    """
    Test that the donation status view requires an order or 404s
    """
    donation_status_url = reverse(
        "donation-status", args=["00000000-0000-0000-0000-000000000000"]
    )

    response = client.get(donation_status_url)
    assert response.status_code == 404


@pytest.mark.django_db()
@pytest.mark.parametrize("status,updated_status", EXPECTED_Updated_STATUS)
def test_donation_status_view(
    client, setup_donation_status_view, status, updated_status
):
    """
    Test that the donation status views response is correct for status
    """
    donation_status_url, donation = setup_donation_status_view
    donation.status = status
    donation.save()

    assert type(donation) is Donation

    response = client.get(donation_status_url)
    assert response.status_code == 200

    assert response.json() == {
        "updatedStatus": updated_status,
        "currentStatus": status,
        "reference": str(donation.reference),
    }
