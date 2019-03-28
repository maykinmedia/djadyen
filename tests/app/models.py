from django.db import models
from djadyen.models import AdyenOrder


class Order(AdyenOrder):
    paid = models.BooleanField(default=False)

    def get_price_in_cents(self):
        return 5000

    def process_authorized_notification(self, notification):
        self.paid = True
        self.save()
