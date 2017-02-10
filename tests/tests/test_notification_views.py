from django.core.urlresolvers import reverse

from djadyen.models import AdyenNotification
from django_webtest import WebTest


class RedirectViewTests(WebTest):
    def setUp(self):
        self.url = reverse('adyen-notifications:notification')

    def test_post_notification_empty(self):
        response = self.app.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '[accepted]')
        self.assertEqual(AdyenNotification.objects.count(), 0)

    def test_post_notification(self):
        params = {
            'eventDate': '2018-01-01T01:02:01.111Z',
            'reason': '58747:1111:6/2018',
            'additionalData.cardSummary': ' 1111',
            'originalReference': '',
            'merchantReference': 'YourMerchantReference1',
            'additionalData.expiryDate': '8/2018',
            'currency': 'EUR',
            'pspReference': '8888777766665555',
            'additionalData.authCode': '58747',
            'merchantAccountCode': 'TestMerchant',
            'eventCode': 'AUTHORISATION',
            'value': '500',
            'operations': 'CANCEL,CAPTURE,REFUND',
            'success': 'true',
            'paymentMethod': 'visa',
            'live': 'false',
        }
        response = self.app.post(self.url, params=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '[accepted]')
        self.assertEqual(AdyenNotification.objects.count(), 1)
