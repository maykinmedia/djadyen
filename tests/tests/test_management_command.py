import json

from django.core.management import call_command
from django.test.testcases import TestCase

import requests_mock

from djadyen.models import AdyenIssuer, AdyenPaymentOption


def json_response(request, context):
    return json.dumps({
        'paymentMethods': [
            {'brandCode': 'mc', 'name': 'MasterCard'},
            {'brandCode': 'visa', 'name': 'VISA'},
            {'brandCode': 'ideal', 'issuers': [
                {'issuerId': '1121', 'name': 'Test Issuer'},
                {'issuerId': '1154', 'name': 'Test Issuer 5'},
                {'issuerId': '1153', 'name': 'Test Issuer 4'},
                {'issuerId': '1152', 'name': 'Test Issuer 3'},
                {'issuerId': '1151', 'name': 'Test Issuer 2'},
                {'issuerId': '1162', 'name': 'Test Issuer Cancelled'},
                {'issuerId': '1161', 'name': 'Test Issuer Pending'},
                {'issuerId': '1160', 'name': 'Test Issuer Refused'},
                {'issuerId': '1159', 'name': 'Test Issuer 10'},
                {'issuerId': '1158', 'name': 'Test Issuer 9'},
                {'issuerId': '1157', 'name': 'Test Issuer 8'},
                {'issuerId': '1156', 'name': 'Test Issuer 7'},
                {'issuerId': '1155', 'name': 'Test Issuer 6'}
            ], 'name': 'iDEAL'}
        ]}, ensure_ascii=False).encode('gbk')


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

    @requests_mock.mock()
    def test_on_empty_database_mock(self, mock):
        mock.post(
            'https://test.adyen.com/hpp/directory.shtml',
            [
                {"content": json_response, "status_code": 200},
            ],
        )

        call_command('sync_payment_methods')

        self.assertEqual(AdyenPaymentOption.objects.count(), 3)
        self.assertEqual(AdyenIssuer.objects.count(), 13)

    @requests_mock.mock()
    def test_on_existing_database_mock(self, mock):
        mock.post(
            'https://test.adyen.com/hpp/directory.shtml',
            [
                {"content": json_response, "status_code": 200},
                {"content": json_response, "status_code": 200},
            ],
        )
        self.assertEqual(AdyenPaymentOption.objects.count(), 0)
        self.assertEqual(AdyenIssuer.objects.count(), 0)

        call_command('sync_payment_methods')

        self.assertEqual(AdyenPaymentOption.objects.count(), 3)
        self.assertEqual(AdyenIssuer.objects.count(), 13)

        call_command('sync_payment_methods')

        self.assertEqual(AdyenPaymentOption.objects.count(), 3)
        self.assertEqual(AdyenIssuer.objects.count(), 13)
