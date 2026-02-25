from djadyen.api import AdyenPaymentDetailsAPI, AdyenPaymentsAPI
from djadyen.choices import Status
from djadyen.views import AdyenAdvancedPaymentView, AdyenPaymentView, AdyenResponseView

from .models import Order


class ConfirmationView(AdyenResponseView):
    template_name = "app/confirmation.html"
    model = Order

    def handle_authorised(self):
        self.order.status = Status.Authorised
        return self.done()

    def handle_pending(self):
        self.order.status = Status.Pending
        return self.done()

    def handle_refused(self):
        self.order.status = Status.Refused
        return self.done()

    def handle_error(self):
        self.order.status = Status.Error
        return self.done()

    def handle_canceled(self):
        self.order.status = Status.Cancel
        return self.done()

    def handle_default(self):
        pass


class PaymentView(AdyenPaymentView):
    template_name = "app/payment.html"
    model = Order

    def get_return_url(self, **kwargs):
        pass


# Web components Advanced view
class AdvancedPaymentView(AdyenAdvancedPaymentView):
    template_name = "app/payment.html"
    model = Order

    def get_return_url(self, **kwargs):
        pass


class PaymentDetailsAPIView(AdyenPaymentDetailsAPI):
    model = Order


class PaymentsAPIView(AdyenPaymentsAPI):
    model = Order
