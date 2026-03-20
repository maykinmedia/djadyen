from djadyen.api import AdyenPaymentDetailsAPI, AdyenPaymentsAPI
from djadyen.choices import Status
from djadyen.views import (
    AdyenAdvancedPaymentView,
    AdyenDonationView,
    AdyenOrderStatusView,
    AdyenPaymentView,
    AdyenResponseView,
)

from .models import Donation, Order

ADYEN_LANGUAGES = {
    "nl": "nl-NL",
    "en": "en-US",
}


class ConfirmationView(AdyenResponseView):
    template_name = "app/confirmation.html"
    model = Order

    def handle_authorised(self):
        self.object.status = Status.Authorised
        self.object.save()

    def handle_error(self):
        self.object.status = Status.Error
        self.object.save()


class PaymentView(AdyenPaymentView):
    template_name = "app/payment.html"
    model = Order

    def get_return_url(self, **kwargs):
        pass


# Web components Advanced view
class AdvancedPaymentView(AdyenAdvancedPaymentView):
    model = Order

    # Map language code to Adyen locale
    def get_locale(self, **kwargs):
        return ADYEN_LANGUAGES.get(self.request.LANGUAGE_CODE, "en-US")

    def get_return_url(self, **kwargs):
        pass


class PaymentDetailsAPIView(AdyenPaymentDetailsAPI):
    model = Order

    def handle_authorised(self):
        self.object.status = Status.Authorised
        self.object.save()


class PaymentsAPIView(AdyenPaymentsAPI):
    model = Order


class DonationView(AdyenDonationView):
    model = Order

    def get_donation_model(self):
        return Donation

    def get_locale(self, **kwargs):
        # Map language code to Adyen locale
        return ADYEN_LANGUAGES.get(self.request.LANGUAGE_CODE, "en-US")

    def handle_authorised(self):
        # save
        self.object.status = Status.Authorised
        self.object.save()

    def get_donation_confirmation_url(self):
        return "reverse self.object.donation"


# Status Order
class OrderStatusView(AdyenOrderStatusView):
    model = Order


class DonationStatusView(AdyenOrderStatusView):
    model = Donation
