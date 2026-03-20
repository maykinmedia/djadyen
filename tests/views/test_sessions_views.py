from django.urls import reverse

import pytest
import requests_mock as rm

from tests.factories import IssuerFactory, OrderFactory, PaymentOptionsFactory

pytestmark = [
    pytest.mark.django_db,
]


def test_session_view_ideal2_redirect_user_to_external_page(django_app, requests_mock: rm.Mocker):
    requests_mock.register_uri(
        rm.ANY,
        rm.ANY,
        json={
            "resultCode": "RedirectShopper",
            "action": {
                "paymentMethodType": "ideal",
                "url": "www.adyen.com/ideal2.0",
                "method": "GET",
                "type": "redirect",
            },
        },
        status_code=200,
    )
    ideal2 = PaymentOptionsFactory.create(adyen_name="ideal")
    order = OrderFactory.create(payment_option=ideal2, issuer=None)
    url = reverse("payment", kwargs={"reference": order.reference})

    response = django_app.get(url)
    assert response.status_code == 302
    assert response.location == "www.adyen.com/ideal2.0"


def test_session_view_ideal2_error_redirect_user_to_confirm_page(
    django_app, requests_mock: rm.Mocker
):
    requests_mock.register_uri(
        rm.ANY,
        rm.ANY,
        status_code=204,
    )
    ideal2 = PaymentOptionsFactory.create(adyen_name="ideal")
    order = OrderFactory.create(payment_option=ideal2, issuer=None)
    url = reverse("payment", kwargs={"reference": order.reference})
    confirm_page = reverse("confirm", kwargs={"reference": order.reference})

    response = django_app.get(url)
    assert response.status_code == 302
    assert response.location == "https://example.com" + confirm_page


def test_session_view_empty_payment_option(django_app, requests_mock: rm.Mocker):
    requests_mock.register_uri(
        rm.ANY,
        rm.ANY,
        status_code=204,
    )

    order = OrderFactory.create(payment_option=None, issuer=None)
    url = reverse("payment", kwargs={"reference": order.reference})

    response = django_app.get(url)
    assert response.status_code == 200


def test_session_view_ideal1_work_flow(django_app, requests_mock: rm.Mocker):
    requests_mock.register_uri(
        rm.ANY,
        rm.ANY,
        status_code=200,
    )
    ideal = PaymentOptionsFactory.create(adyen_name="ideal")
    issuer = IssuerFactory.create(payment_option=ideal)
    order = OrderFactory.create(payment_option=ideal, issuer=issuer)
    url = reverse("payment", kwargs={"reference": order.reference})

    response = django_app.get(url)
    assert response.status_code == 200
