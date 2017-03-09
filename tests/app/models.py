from djadyen.models import AdyenOrder


class Order(AdyenOrder):
    def get_price_in_cents(self):
        return 5000
