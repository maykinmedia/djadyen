from django.test import override_settings
from django.urls import reverse

from django_webtest import WebTest
from webtest import AppError

from djadyen import settings

from .factories import IssuerFactory, OrderFactory, PaymentOptionsFactory


class ConfirmationView(WebTest):
    def setUp(self):
        self.order = OrderFactory()
        self.url = reverse('confirm')

    def _get_csrf_token(self):
        url = reverse('redirect', kwargs={'reference': self.order.reference})
        response = self.app.get(url)
        return response.forms[0]['csrfmiddlewaretoken'].value

    def test_empty_get(self):
        with self.assertRaises(AppError):
            self.app.get(self.url)

    def test_error_response(self):
        params = {
            "redirectResult": "handle_error"
        }
        response = self.app.get(self.url, params=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '\n    Success!\n\n')

    def test_cancelled_response(self):
        params = {
            "redirectResult": "handle_cancelled"
        }
        response = self.app.get(self.url, params=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '\n    Success!\n\n')

    def test_refused_response(self):
        params = {
            "redirectResult": "handle_refused"
        }
        response = self.app.get(self.url, params=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '\n    Success!\n\n')

    def test_pending_response(self):
        params = {
            "redirectResult": "handle_pending"
        }
        response = self.app.get(self.url, params=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '\n    Success!\n\n')

    def test_authorised_response(self):
        params = {
            "redirectResult": "handle_authorised"
        }
        response = self.app.get(self.url, params=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '\n    Success!\n\n')

    def test_post(self):
        params = {
            "redirectResult": "handle_authorised"
        }
        params['csrfmiddlewaretoken'] = self._get_csrf_token()
        response = self.app.post(self.url, params=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '\n    Success!\n\n')
