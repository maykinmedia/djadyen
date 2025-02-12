from django.test import RequestFactory
from django.urls import reverse

import requests_mock
from django_webtest import WebTest

from .factories import IssuerFactory, OrderFactory, PaymentOptionsFactory
from .utils import TestFileMixin


class ConfirmationView(TestFileMixin, WebTest):
    def setUp(self):
        super().setUp()
        self.order = OrderFactory()
        self.url = reverse("confirm", kwargs={"reference": self.order.reference})
        self.params = {"redirectResult": "something"}

    def test_empty_get(self):
        self.app.get(self.url, status=200)


class PaymentViewTest(WebTest):
    @requests_mock.Mocker()
    def test_ideal2_redirect_user_to_external_page(self, m: requests_mock.Mocker):
        m.register_uri(
            requests_mock.ANY,
            requests_mock.ANY,
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

        response = self.app.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "www.adyen.com/ideal2.0")

    @requests_mock.Mocker()
    def test_ideal2_error_redirect_user_to_confirm_page(self, m: requests_mock.Mocker):
        m.register_uri(
            requests_mock.ANY,
            requests_mock.ANY,
            status_code=204,
        )
        ideal2 = PaymentOptionsFactory.create(adyen_name="ideal")
        order = OrderFactory.create(payment_option=ideal2, issuer=None)
        url = reverse("payment", kwargs={"reference": order.reference})
        confirm_page = reverse("confirm", kwargs={"reference": order.reference})

        response = self.app.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "https://example.com" + confirm_page)

    @requests_mock.Mocker()
    def test_empty_payment_option(self, m: requests_mock.Mocker):
        m.register_uri(
            requests_mock.ANY,
            requests_mock.ANY,
            status_code=204,
        )
        ideal2 = PaymentOptionsFactory.create(adyen_name="ideal")
        order = OrderFactory.create(payment_option=None, issuer=None)
        url = reverse("payment", kwargs={"reference": order.reference})
        confirm_page = reverse("confirm", kwargs={"reference": order.reference})

        response = self.app.get(url)
        self.assertEqual(response.status_code, 200)

    @requests_mock.Mocker()
    def test_ideal1_work_flow(self, m: requests_mock.Mocker):
        m.register_uri(
            requests_mock.ANY,
            requests_mock.ANY,
            status_code=200,
        )
        ideal = PaymentOptionsFactory.create(adyen_name="ideal")
        issuer = IssuerFactory.create(payment_option=ideal)
        order = OrderFactory.create(payment_option=ideal, issuer=issuer)
        url = reverse("payment", kwargs={"reference": order.reference})

        response = self.app.get(url)
        self.assertEqual(response.status_code, 200)
