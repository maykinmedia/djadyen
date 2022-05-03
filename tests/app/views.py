from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView

from djadyen.choices import Status
from djadyen.hpp import HPPPaymenRequest
from djadyen.views import AdyenRedirectView, AdyenResponseMixin

from .models import Order


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
