from django.urls import reverse

import pytest
import requests_mock as rm

from djadyen.choices import Status
from tests.factories import IssuerFactory, OrderFactory, PaymentOptionsFactory

pytestmark = [
    pytest.mark.django_db,
]


def test_session_dropin_view_ideal1_work_flow(django_app, requests_mock: rm.Mocker):
    requests_mock.register_uri(
        rm.ANY,
        rm.ANY,
        status_code=200,
    )
    ideal = PaymentOptionsFactory.create(adyen_name="ideal")
    issuer = IssuerFactory.create(payment_option=ideal)
    order = OrderFactory.create(payment_option=ideal, issuer=issuer)
    url = reverse("session-dropin", kwargs={"reference": order.reference})

    response = django_app.get(url)
    assert response.status_code == 200


def test_session_dropin_view_free_order(django_app):
    order = OrderFactory(amount=0, status=Status.Pending)
    url = reverse("session-dropin", kwargs={"reference": order.reference})
    response = django_app.get(url, status=302)

    assert response.url == order.get_return_url()

    order.refresh_from_db()
    # Order is finished in the redirect view
    assert order.status == Status.Pending
