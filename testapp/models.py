from django.db import models
from django.urls import reverse

from djadyen.models import AdyenOrder


class Order(AdyenOrder):
    paid = models.BooleanField(default=False)

    def get_price_in_cents(self):
        return 5000

    def process_notification(self, notification):
        super().process_notification(notification)

        if notification.is_authorised():
            self.paid = True
            self.save()

    def get_return_url(self):
        return "{host}{path}".format(
            host="https://example.com",
            path=reverse("confirm", kwargs={"reference": self.reference}),
        )

    def get_redirect_url(self):
        return "{host}{path}".format(
            host="https://example.com",
            path=reverse("redirect", kwargs={"reference": self.reference}),
        )
