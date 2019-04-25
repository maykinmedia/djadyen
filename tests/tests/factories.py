import factory

from djadyen.choices import Status
from djadyen.models import AdyenIssuer, AdyenNotification, AdyenPaymentOption

from ..app.models import Order


class NotificationFactory(factory.DjangoModelFactory):
    class Meta:
        model = AdyenNotification


class PaymentOptionsFactory(factory.DjangoModelFactory):
    name = factory.Faker('name')
    adyen_name = 'ideal'
    guid = 'ee112bdd-b03b-422f-8af2-085c64dd8698'

    class Meta:
        model = AdyenPaymentOption


class IssuerFactory(factory.DjangoModelFactory):
    payment_option = factory.SubFactory(PaymentOptionsFactory)
    name = factory.Faker('name')
    adyen_id = 1155

    class Meta:
        model = AdyenIssuer


class OrderFactory(factory.DjangoModelFactory):
    status = Status.Created
    email = factory.Faker('email')

    class Meta:
        model = Order
