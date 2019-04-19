from django.db import models
from djadyen.models import AdyenOrder


class Order(AdyenOrder):
    paid = models.BooleanField(default=False)

    def get_price_in_cents(self):
        return 5000

    def process_notification(self, notification):
        super(Order, self).process_notification(notification)
        if notification.is_authorised():
            self.paid = True
            self.save()
