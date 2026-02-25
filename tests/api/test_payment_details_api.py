import json

from django.urls import reverse

import pytest

from djadyen.choices import Status


@pytest.mark.django_db()
def test_payment_details_api_no_order(client):
    payment_details_api_url = reverse(
        "payment_details_api", args=["00000000-0000-0000-0000-000000000000"]
    )

    response = client.post(payment_details_api_url)
    assert response.status_code == 404


@pytest.mark.django_db()
def test_payment_details_api_require_post(client, payment_details_api):
    url, order = payment_details_api
    response = client.get(url)

    order.refresh_from_db()
    assert response.status_code == 405
    assert order.status == Status.Created


@pytest.mark.django_db()
def test_payment_details_api_empty_request(
    client,
    payment_details_api,
):
    url, order = payment_details_api
    response = client.post(url)

    order.refresh_from_db()
    assert response.status_code == 400
    assert response.json() == {"error": "bad response"}
    assert order.status == Status.Created


@pytest.mark.django_db()
def test_payment_details_api_simple(
    client, payment_details_api, mock_successful_payment_details_api
):
    url, order = payment_details_api
    data = json.dumps({"paymentMethod": "data"})
    response = client.post(url, data=data, content_type="application/json")

    order.refresh_from_db()
    assert response.status_code == 200
    assert response.json() == {
        "resultCode": "Authorised",
        "action": None,
        "order": None,
        "donationToken": "EXAMPLE_DONATION_TOKEN",
    }
    assert order.donation_token == "EXAMPLE_DONATION_TOKEN"
    assert order.status == Status.Pending
    assert order.psp_reference == "V4HZ4RBFJGXXGN82"
