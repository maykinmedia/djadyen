from django.core.management import call_command
from django.test.testcases import TestCase

from djadyen.models import AdyenIssuer, AdyenPaymentOption


class SyncPaymentMethods(TestCase):
    def test_on_empty_database(self):
        self.assertEqual(AdyenPaymentOption.objects.count(), 0)
        self.assertEqual(AdyenIssuer.objects.count(), 0)

        with self.assertRaises(ValueError):
            call_command('sync_payment_methods')

        # self.assertEqual(AdyenPaymentOption.objects.count(), 3)
        # self.assertEqual(AdyenIssuer.objects.count(), 13)

    def test_on_existing_database(self):
        self.assertEqual(AdyenPaymentOption.objects.count(), 0)
        self.assertEqual(AdyenIssuer.objects.count(), 0)

        with self.assertRaises(ValueError):
            call_command('sync_payment_methods')

        # self.assertEqual(AdyenPaymentOption.objects.count(), 3)
        # self.assertEqual(AdyenIssuer.objects.count(), 13)

        # call_command('sync_payment_methods')

        # self.assertEqual(AdyenPaymentOption.objects.count(), 3)
        # self.assertEqual(AdyenIssuer.objects.count(), 13)
