from django.urls import reverse

import requests_mock
from django_webtest import WebTest

from .factories import OrderFactory
from .utils import TestFileMixin


class ConfirmationView(TestFileMixin, WebTest):
    def setUp(self):
        super().setUp()
        self.order = OrderFactory()
        self.url = reverse("confirm", kwargs={"reference": self.order.reference})
        self.params = {"redirectResult": "something"}

    def test_empty_get(self):
        self.app.get(self.url, status=404)

    @requests_mock.mock()
    def test_cancelled_response(self, mock):
        mock.post(
            "https://checkout-test.adyen.com/v69/payments/details",
            [
                {
                    "content": self._get_test_file("payment_cancelled.json").read(),
                    "status_code": 200,
                },
            ],
        )
        response = self.app.get(self.url, params=self.params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "\n    Success!\n\n")
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "cancel")

    @requests_mock.mock()
    def test_refused_response(self, mock):
        mock.post(
            "https://checkout-test.adyen.com/v69/payments/details",
            [
                {
                    "content": self._get_test_file("payment_refused.json").read(),
                    "status_code": 200,
                },
            ],
        )
        response = self.app.get(self.url, params=self.params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "\n    Success!\n\n")
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "refused")

    @requests_mock.mock()
    def test_pending_response(self, mock):
        mock.post(
            "https://checkout-test.adyen.com/v69/payments/details",
            [
                {
                    "content": self._get_test_file("payment_pending.json").read(),
                    "status_code": 200,
                },
            ],
        )
        response = self.app.get(self.url, params=self.params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "\n    Success!\n\n")
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "pending")

    @requests_mock.mock()
    def test_authorised_response(self, mock):
        mock.post(
            "https://checkout-test.adyen.com/v69/payments/details",
            [
                {
                    "content": self._get_test_file("payment_success.json").read(),
                    "status_code": 200,
                },
            ],
        )
        response = self.app.get(self.url, params=self.params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "\n    Success!\n\n")
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "authorised")
