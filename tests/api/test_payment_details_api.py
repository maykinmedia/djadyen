import json

from django.urls import reverse

import pytest

from djadyen.choices import Status


@pytest.mark.django_db()
def test_payment_details_api_not_implemented_error():
    """
    Test AdyenPaymentDetailsAPI required implemented functions
    :return:
    """
    from djadyen.api import AdyenPaymentDetailsAPI

    with pytest.raises(NotImplementedError):
        AdyenPaymentDetailsAPI().handle_authorised()


@pytest.mark.django_db()
def test_payment_details_api_no_order(client):
    payment_details_api_url = reverse(
        "payment_details_api", args=["00000000-0000-0000-0000-000000000000"]
    )

    response = client.post(payment_details_api_url)
    assert response.status_code == 404


@pytest.mark.django_db()
def test_payment_details_api_require_post(client, setup_payment_details_api):
    url, order = setup_payment_details_api
    response = client.get(url)

    order.refresh_from_db()
    assert response.status_code == 405
    assert order.status == Status.Created


@pytest.mark.django_db()
def test_payment_details_api_empty_request(
    client,
    setup_payment_details_api,
):
    url, order = setup_payment_details_api
    response = client.post(url)

    order.refresh_from_db()
    assert response.status_code == 400
    assert response.json() == {"error": "bad response"}
    assert order.status == Status.Created


@pytest.mark.django_db()
def test_payment_details_api_simple(
    client, setup_payment_details_api, mock_successful_payment_details_api
):
    url, order = setup_payment_details_api
    data = json.dumps({"paymentMethod": "data"})
    response = client.post(url, data=data, content_type="application/json")

    order.refresh_from_db()
    assert response.status_code == 200
    assert response.json() == {
        "resultCode": "Authorised",
        "action": None,
        "order": None,
        "donationToken": "DONATION_IDEAL_TOKEN",
    }
    assert order.donation_token == "DONATION_IDEAL_TOKEN"
    assert order.status == Status.Authorised
    assert order.psp_reference == "PSP_EXAMPLE_IDEAL"


@pytest.mark.django_db()
def test_payment_details_api_redirect(
    client, setup_payment_details_api, mock_redirect_payment_details_api
):
    url, order = setup_payment_details_api
    order.status = Status.Pending
    order.save()

    data = json.dumps({"paymentMethod": "data"})
    response = client.post(url, data=data, content_type="application/json")

    order.refresh_from_db()
    assert response.status_code == 200
    assert response.json() == {
        "resultCode": "RedirectShopper",
        "action": {
            "paymentMethodType": "ideal",
            "url": "https://test.adyen.com/hpp/checkout.shtml",
            "method": "GET",
            "type": "redirect",
        },
        "order": None,
        "donationToken": None,
    }
    assert order.status == Status.Pending
    assert order.psp_reference == ""


@pytest.mark.django_db()
def test_payment_details_api_failed_payment(
    client, setup_payment_details_api, mock_refused_payment_details_api
):
    url, order = setup_payment_details_api
    data = json.dumps({"paymentMethod": "data"})
    response = client.post(url, data=data, content_type="application/json")

    order.refresh_from_db()
    assert response.status_code == 200
    assert response.json() == {
        "resultCode": "Refused",
        "action": None,
        "order": None,
        "donationToken": None,
    }
    assert order.status == Status.Refused
    assert order.psp_reference == "PSP_EXAMPLE_IDEAL"


@pytest.mark.django_db()
def test_payment_details_api_exception(
    client, setup_payment_details_api, mock_payment_details_api_exception
):
    url, order = setup_payment_details_api
    data = json.dumps({"paymentMethod": "data"})
    response = client.post(url, data=data, content_type="application/json")

    order.refresh_from_db()
    assert response.status_code == 400
    assert response.json() == {"error": "bad response"}
    assert order.donation_token == ""
    assert order.status == Status.Error
    assert order.psp_reference == "PSP_EXAMPLE"
    assert "Adyen API /payment/details/" in order.status_message
