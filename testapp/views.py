from djadyen.api import AdyenPaymentDetailsAPI, AdyenPaymentsAPI
from djadyen.choices import Status
from djadyen.views import (
    AdyenAdvancedPaymentView,
    AdyenDonationView,
    AdyenResponseView,
    AdyenSessionPaymentView,
    AdyenStatusView,
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


class PaymentView(AdyenSessionPaymentView):
    template_name = "app/payment.html"
    model = Order


# Web components Advanced view
class AdvancedPaymentView(AdyenAdvancedPaymentView):
    model = Order

    # Map language code to Adyen locale
    def get_locale(self, **kwargs):
        return ADYEN_LANGUAGES.get(self.request.LANGUAGE_CODE, "en-US")


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
class OrderStatusView(AdyenStatusView):
    model = Order


class DonationStatusView(AdyenStatusView):
    model = Donation
