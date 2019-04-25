import json
from datetime import datetime
from uuid import uuid4

from django.core.management import call_command
from django.test.testcases import TestCase

import requests_mock
from freezegun import freeze_time

from djadyen import settings
from djadyen.choices import Status
from djadyen.models import AdyenIssuer, AdyenPaymentOption

from .factories import NotificationFactory, OrderFactory


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


class ProcessNotifications(TestCase):
    def setUp(self):
        super(ProcessNotifications, self).setUp()

        reference = str(uuid4())

        data = {
            'success': 'true',
            'eventCode': 'AUTHORISATION',
            'merchantReference': reference,
            'merchantAccountCode': settings.ADYEN_MERCHANT_ACCOUNT,
        }

        self.notification1 = NotificationFactory.create(
            notification=json.dumps(data),
            is_processed=False
        )
        self.order1 = OrderFactory.create(
            status=Status.Pending,
            reference=reference
        )

    @freeze_time('2019-01-01 12:00')
    def test_process_notifications_already_processed(self):
        """
        Make sure that an order, which status has already been
        set as 'Authorised' is not processed again.
        """
        self.order1.status = Status.Authorised
        self.order1.save()

        self.assertFalse(self.order1.paid)

        call_command('adyen_maintenance')

        self.order1.refresh_from_db()
        self.assertFalse(self.order1.paid)

    @freeze_time('2019-01-01 12:00')
    def test_process_notifications(self):
        self.assertFalse(self.order1.paid)

        call_command('adyen_maintenance')

        self.order1.refresh_from_db()
        self.assertTrue(self.order1.paid)

        self.notification1.refresh_from_db()
        self.assertTrue(self.notification1.is_processed)
        self.assertTrue(self.notification1.processed_at, datetime(2019, 1, 1, 12, 0))


class CleanupPending(TestCase):
    def test_cleanup(self):
        # 5 days ago; Should be marked as 'Error'
        with freeze_time('2019-01-5 12:00'):
            self.order1 = OrderFactory.create(status=Status.Pending)
        # 4 days ago; Should be left alone
        with freeze_time('2019-01-6 12:00'):
            self.order2 = OrderFactory.create(status=Status.Pending)
        # 6 days ago, Should be marked as 'Error'
        with freeze_time('2019-01-4 12:00'):
            self.order3 = OrderFactory.create(status=Status.Pending)
        # 7 days ago, but Authorised, should be left alone
        with freeze_time('2019-01-3 12:00'):
            self.order4 = OrderFactory.create(status=Status.Authorised)

        with freeze_time('2019-01-10 12:00'):
            call_command('adyen_maintenance')

        self.order1.refresh_from_db()
        self.order2.refresh_from_db()
        self.order3.refresh_from_db()
        self.order4.refresh_from_db()

        self.assertEqual(self.order1.status, Status.Error)
        self.assertEqual(self.order2.status, Status.Pending)
        self.assertEqual(self.order3.status, Status.Error)
        self.assertEqual(self.order4.status, Status.Authorised)
