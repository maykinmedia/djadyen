
import json
from django.urls import reverse

from django_webtest import WebTest

from djadyen.models import AdyenNotification


class NotificationViewTests(WebTest):
    def setUp(self):
        self.url = reverse('adyen-notifications:notification')

        self.post_data = {
            'additionalData.hmacSignature': 'sJPOWBVc8nZRBX8/6xW8hsqyo381D8nsDkVThu++9LU=',
            'merchantAccountCode': 'MaykinMediaNL',
            'live': 'false',
            'originalReference': '',
            'paymentMethod': 'ideal',
            'value': '350',
            'pspReference': '8515535308218301',
            'operations': 'REFUND',
            'eventDate': '2019-03-25T16:20:23.71Z',
            'success': 'true',
            'currency': 'EUR',
            'merchantReference': '2b947321-527c-4b69-9cca-1f278cb4b23b',
            'eventCode': 'AUTHORISATION',
        }

    def test_post_notification_empty_hmac(self):
        """
        An empty hmac signature is always a nice edge case.
        """
        params = {
            'additionalData.hmacSignature': '',
        }
        response = self.app.post(self.url, params=params, status=403)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(AdyenNotification.objects.count(), 0)

    def test_post_notification_no_hmac(self):
        """
        Make sure that a notification without a HMAC set, does not work.
        """
        del self.post_data['additionalData.hmacSignature']
        response = self.app.post(self.url, params=self.post_data, status=403)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(AdyenNotification.objects.count(), 0)

    def test_hmac_verification_invalid_hmac(self):
        self.post_data['additionalData.hmacSignature'] += 'x'
        response = self.app.post(self.url, self.post_data, status=403)
        self.assertEqual(response.status_code, 403)
        self.assertFalse(AdyenNotification.objects.exists())

    def test_hmac_verification(self):
        self.app.post(self.url, params=self.post_data)
        self.assertTrue(AdyenNotification.objects.exists())

        notification = AdyenNotification.objects.get()
        self.assertEqual(json.loads(notification.notification), self.post_data)
