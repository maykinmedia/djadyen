from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView

from djadyen.choices import Status
from djadyen.hpp import HPPPaymenRequest
from djadyen.views import AdyenRedirectView, AdyenResponseMixin

from .models import Order


class MyAdyenRequestView(AdyenRedirectView):
    model = Order

    def get_next_url(self):  # This is to populate the resURL
        return reverse('confirm')


class My2AdyenRequestView(AdyenRedirectView):
    model = Order

    def get_payment_request(self, obj):
        payment_request = HPPPaymenRequest.from_object(obj, self.get_next_url())
        payment_request.ship_before_date = timezone.now()
        payment_request.merchant_return_data = 'returnData'
        return payment_request

    def get_next_url(self):
        return ''


class My3AdyenRequestView(AdyenRedirectView):
    model = Order

    def get_payment_request(self, obj):
        payment_request = HPPPaymenRequest.from_object(obj, self.get_next_url())
        payment_request.ship_before_date = timezone.now()
        payment_request.merchant_return_data = 'returnData'
        return payment_request

    def can_skip_payment(self):
        return True


class ConfirmationView(AdyenResponseMixin, TemplateView):
    template_name = 'app/confirmation.html'
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
        if self.payment_response.psp_reference:
            self.order.psp_reference = self.payment_response.psp_reference


class Confirmation2View(AdyenResponseMixin, TemplateView):
    template_name = 'app/confirmation.html'
    model = Order
