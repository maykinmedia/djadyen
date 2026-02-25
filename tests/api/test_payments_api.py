import json

from django.urls import reverse

import pytest

from djadyen.choices import Status


@pytest.mark.django_db()
def test_payments_api_no_order(client):
    payments_api_url = reverse(
        "payments_api", args=["00000000-0000-0000-0000-000000000000"]
    )

    response = client.post(payments_api_url)
    assert response.status_code == 404


@pytest.mark.django_db()
def test_payments_api_require_post(client, payments_api):
    url, order = payments_api
    response = client.get(url)

    order.refresh_from_db()
    assert response.status_code == 405
    assert order.status == Status.Created


@pytest.mark.django_db()
def test_payments_api_empty_request(
    client,
    payments_api,
):
    url, order = payments_api
    response = client.post(url)

    order.refresh_from_db()
    assert response.status_code == 400
    assert response.json() == {"error": "bad response"}
    assert order.status == Status.Created


@pytest.mark.django_db()
def test_payments_api_no_payment_method(client, payments_api):
    url, order = payments_api
    data = json.dumps({"unrelated": "data"})
    response = client.post(url, data, content_type="application/json")

    order.refresh_from_db()
    assert response.status_code == 400
    assert response.json() == {"error": "bad response"}
    assert order.status == Status.Created


@pytest.mark.django_db()
def test_payments_api_simple(client, payments_api, mock_successful_payments_api):
    url, order = payments_api
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
    assert order.status == Status.Pending
    assert order.psp_reference == "993617895215577D"
    assert order.donation_token == "EXAMPLE_DONATION_TOKEN"


@pytest.mark.django_db()
def test_payments_api_redirect(client, payments_api, mock_redirect_ideal_payments_api):
    url, order = payments_api
    data = json.dumps({"paymentMethod": "data"})
    response = client.post(url, data=data, content_type="application/json")

    json_response = response.json()

    order.refresh_from_db()
    assert response.status_code == 200
    assert json_response["resultCode"] == "RedirectShopper"
    assert json_response["action"]["type"] == "redirect"
    assert json_response["action"]["paymentMethodType"] == "ideal"
    assert order.status == Status.Pending

    # psp reference is only set on payment
    assert order.psp_reference == ""
    assert order.donation_token == ""
