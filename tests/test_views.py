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
        self.app.get(self.url, status=200)
