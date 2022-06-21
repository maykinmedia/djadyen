import json
from django.urls import reverse

from django_webtest import WebTest

from djadyen.models import AdyenNotification

from .utils import TestFileMixin


class NotificationViewTests(TestFileMixin, WebTest):
    def setUp(self):
        super().setUp()
        self.url = reverse("adyen-notifications:notification")

    def test_success_data(self):
        self.app.post_json(
            self.url,
            json.loads(self._get_json_data("notification_success.json")),
        )
        self.assertEqual(AdyenNotification.objects.count(), 1)

        notification = AdyenNotification.objects.get()
        self.assertIsNotNone(notification.notification)

    def test_unsuccessful_data(self):
        self.app.post_json(
            self.url,
            json.loads(self._get_json_data("notification_unsuccessful.json")),
        )
        self.assertEqual(AdyenNotification.objects.count(), 1)

        notification = AdyenNotification.objects.get()
        self.assertIsNotNone(notification.notification)

    def test_multiple_data(self):
        self.app.post_json(
            self.url,
            json.loads(self._get_json_data("notification_multiple.json")),
        )
        self.assertEqual(AdyenNotification.objects.count(), 3)
