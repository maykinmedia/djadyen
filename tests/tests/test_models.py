from django.test import TestCase, override_settings

from djadyen import settings
from djadyen.choices import Status

from .factories import (
    IssuerFactory, NotificationFactory, OrderFactory, PaymentOptionsFactory
)


class AdyenNofiticationTests(TestCase):
    def test_str(self):
        notification = NotificationFactory()
        self.assertEqual(notification.__str__(), notification.created_at.strftime('%c'))


class AdyenOrderTests(TestCase):
    def test_str(self):
        with self.assertNumQueries(1):
            order = OrderFactory()
            self.assertEqual(order.__str__(), '{}'.format(order.reference))

    @override_settings(ADYEN_REFETCH_OLD_STATUS=True)
    def test_refetch_old_status(self):
        with self.assertNumQueries(3):
            order = OrderFactory()
            self.assertEqual(order.__str__(), '{}'.format(order.reference))

            order.status = Status.Authorised
            order.save()
            self.assertEqual(order.__str__(), '{}'.format(order.reference))

    def test_can_not_overwrite_authorised_status(self):
        with self.assertNumQueries(2):
            order = OrderFactory(status=Status.Authorised)
            self.assertEqual(order.status, 'authorised')

            order.status = Status.Cancel
            order.save()
            self.assertEqual(order.status, 'authorised')


class AdyenIssuerTests(TestCase):
    def test_str(self):
        issuer = IssuerFactory()
        self.assertEqual(issuer.__str__(), issuer.name)


class AdyenPaymentOptionTests(TestCase):
    def test_str(self):
        payment_option = PaymentOptionsFactory()
        self.assertEqual(payment_option.__str__(), payment_option.name)
