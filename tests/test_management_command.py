import json
import os
from datetime import datetime
from uuid import uuid4

from django.core.management import call_command
from django.test.testcases import TestCase

import requests_mock
from freezegun import freeze_time

from djadyen.choices import Status
from djadyen.models import AdyenIssuer, AdyenPaymentOption

from .factories import NotificationFactory, OrderFactory
from .utils import TestFileMixin


class SyncPaymentMethods(TestFileMixin, TestCase):
    @requests_mock.mock()
    def test_on_empty_database_mock(self, mock):
        mock.post(
            "https://checkout-test.adyen.com/v71/paymentMethods",
            [
                {
                    "content": self._get_test_file("payment_methods.json").read(),
                    "status_code": 200,
                },
            ],
        )

        call_command("sync_payment_methods")

        self.assertEqual(AdyenPaymentOption.objects.count(), 14)
        self.assertEqual(AdyenIssuer.objects.count(), 47)

    @requests_mock.mock()
    def test_on_existing_database_mock(self, mock):
        mock.post(
            "https://checkout-test.adyen.com/v71/paymentMethods",
            [
                {
                    "content": self._get_test_file("payment_methods.json").read(),
                    "status_code": 200,
                },
                {
                    "content": self._get_test_file("payment_methods.json").read(),
                    "status_code": 200,
                },
            ],
        )
        self.assertEqual(AdyenPaymentOption.objects.count(), 0)
        self.assertEqual(AdyenIssuer.objects.count(), 0)

        call_command("sync_payment_methods")

        self.assertEqual(AdyenPaymentOption.objects.count(), 14)
        self.assertEqual(AdyenIssuer.objects.count(), 47)

        call_command("sync_payment_methods")

        self.assertEqual(AdyenPaymentOption.objects.count(), 14)
        self.assertEqual(AdyenIssuer.objects.count(), 47)


class ProcessNotifications(TestFileMixin, TestCase):
    def setUp(self):
        super().setUp()

        reference = "93ca495f-3b85-4df7-aeb0-052194014c2e"

        with freeze_time("2019-01-01 11:44"):
            self.notification1 = NotificationFactory.create(
                notification=self._get_json_data("notification_data_success.json"),
                is_processed=False,
            )
        self.order1 = OrderFactory.create(status=Status.Pending, reference=reference)

    @freeze_time("2019-01-01 12:00")
    def test_process_notifications_already_processed(self):
        """
        Make sure that an order, which status has already been
        set as 'Authorised' is not processed again.
        """
        self.order1.status = Status.Authorised
        self.order1.save()

        self.assertFalse(self.order1.paid)

        call_command("adyen_maintenance")

        self.order1.refresh_from_db()
        self.assertFalse(self.order1.paid)

    @freeze_time("2019-01-01 12:00")
    def test_process_notifications(self):
        self.assertFalse(self.order1.paid)

        call_command("adyen_maintenance")

        self.order1.refresh_from_db()
        self.assertTrue(self.order1.paid)

        self.notification1.refresh_from_db()
        self.assertTrue(self.notification1.is_processed)
        self.assertTrue(self.notification1.processed_at, datetime(2019, 1, 1, 12, 0))

    @freeze_time("2019-01-01 12:00")
    def test_process_notifications_unsuccessful(self):
        self.assertFalse(self.order1.paid)

        self.notification1.notification = self._get_json_data(
            "notification_data_unsuccessful.json"
        )
        self.notification1.save()

        call_command("adyen_maintenance")

        self.order1.refresh_from_db()
        self.assertFalse(self.order1.paid)

        self.notification1.refresh_from_db()
        self.assertTrue(self.notification1.is_processed)
        self.assertTrue(self.notification1.processed_at, datetime(2019, 1, 1, 12, 0))


class CleanupPending(TestFileMixin, TestCase):
    def test_cleanup(self):
        # 5 days ago; Should be marked as 'Error'
        with freeze_time("2019-01-5 12:00"):
            self.order1 = OrderFactory.create(status=Status.Pending)
        # 4 days ago; Should be left alone
        with freeze_time("2019-01-6 12:00"):
            self.order2 = OrderFactory.create(status=Status.Pending)
        # 6 days ago, Should be marked as 'Error'
        with freeze_time("2019-01-4 12:00"):
            self.order3 = OrderFactory.create(status=Status.Pending)
        # 7 days ago, but Authorised, should be left alone
        with freeze_time("2019-01-3 12:00"):
            self.order4 = OrderFactory.create(status=Status.Authorised)

        with freeze_time("2019-01-01 11:44"):
            self.notification1 = NotificationFactory.create(
                notification=self._get_json_data(
                    "notification_data_reference_unknown.json"
                ),
                is_processed=False,
            )

        with freeze_time("2019-01-10 12:00"):
            call_command("adyen_maintenance")

        self.order1.refresh_from_db()
        self.order2.refresh_from_db()
        self.order3.refresh_from_db()
        self.order4.refresh_from_db()
        self.notification1.refresh_from_db()

        self.assertEqual(self.order1.status, Status.Error)
        self.assertEqual(self.order2.status, Status.Pending)
        self.assertEqual(self.order3.status, Status.Error)
        self.assertEqual(self.order4.status, Status.Authorised)
        self.assertTrue(self.notification1.is_processed)
