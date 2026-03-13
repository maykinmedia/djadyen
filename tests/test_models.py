from django.test import TestCase, override_settings

import pytest

from djadyen.choices import Status

from .factories import (
    IssuerFactory,
    NotificationFactory,
    OrderFactory,
    PaymentOptionsFactory,
)


def test_order_model_required_implements():
    from testapp.models import BadOrderModel

    order = BadOrderModel()

    with pytest.raises(NotImplementedError):
        order.get_return_url()

    order.get_return_url = lambda: "https://example.com/get_return_url"

    with pytest.warns(UserWarning) as record:
        url = order.get_redirect_url()
        assert url == "https://example.com/get_return_url"

    assert len(record) == 1
    assert (
        record[0].message.args[0]
        == "Implement the payment redirect used in the advanced checkout on the "
        "'BadOrderModel'. By default, it will redirect to get_redirect_url"
    )


class AdyenNofiticationTests(TestCase):
    def test_str(self):
        notification = NotificationFactory()
        self.assertEqual(notification.__str__(), notification.created_at.strftime("%c"))


class AdyenOrderTests(TestCase):
    def test_str(self):
        with self.assertNumQueries(1):
            order = OrderFactory()
            self.assertEqual(order.__str__(), f"{order.reference}")

    @override_settings(ADYEN_REFETCH_OLD_STATUS=True)
    def test_refetch_old_status(self):
        with self.assertNumQueries(2):
            order = OrderFactory()
            self.assertEqual(order.__str__(), f"{order.reference}")

            order.status = Status.Authorised
            order.save()
            self.assertEqual(order.__str__(), f"{order.reference}")

    def test_can_not_overwrite_authorised_status(self):
        with self.assertNumQueries(2):
            order = OrderFactory(status=Status.Authorised)
            self.assertEqual(order.status, "Authorised")

            order.status = Status.Cancel
            order.save()
            self.assertEqual(order.status, "Authorised")


class AdyenIssuerTests(TestCase):
    def test_str(self):
        issuer = IssuerFactory()
        self.assertEqual(issuer.__str__(), issuer.name)


class AdyenPaymentOptionTests(TestCase):
    def test_str(self):
        payment_option = PaymentOptionsFactory()
        self.assertEqual(payment_option.__str__(), payment_option.name)
