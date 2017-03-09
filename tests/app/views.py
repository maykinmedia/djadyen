from django.core.urlresolvers import reverse
from django.utils import timezone
from django.views.generic import TemplateView

from djadyen.choices import Status
from djadyen.views import AdyenRedirectView, AdyenResponseMixin

from .models import Order


class MyAdyenRequestView(AdyenRedirectView):
    model = Order

    def get_form_kwargs(self):
        order = self.get_object()
        params = self.get_signed_order_params(order)

        kwargs = super(MyAdyenRequestView, self).get_form_kwargs()
        kwargs.update({'initial': params})
        return kwargs

    def get_next_url(self):  # This is to populate the resURL
        return reverse('confirm')


class My2AdyenRequestView(AdyenRedirectView):
    model = Order

    def get_form_kwargs(self):
        params = self.get_default_params(
            shipBeforeDate=timezone.now(), merchantReturnData='returnData')

        kwargs = super(My2AdyenRequestView, self).get_form_kwargs()
        kwargs.update({'initial': params})
        return kwargs


class My3AdyenRequestView(AdyenRedirectView):
    model = Order

    def get_form_kwargs(self):
        params = self.get_default_params(
            shipBeforeDate=timezone.now(), merchantReturnData='returnData')

        kwargs = super(My3AdyenRequestView, self).get_form_kwargs()
        kwargs.update({'initial': params})
        return kwargs

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
        if self.psp_reference:
            self.order.psp_reference = self.psp_reference


class Confirmation2View(AdyenResponseMixin, TemplateView):
    template_name = 'app/confirmation.html'
    auto_fetch = False


class Confirmation3View(AdyenResponseMixin, TemplateView):
    template_name = 'app/confirmation.html'
    auto_fetch = False

    def handle_authorised(self):
        return self.done()

    def handle_pending(self):
        return self.done()

    def handle_refused(self):
        return self.done()

    def handle_error(self):
        return self.done()

    def handle_canceled(self):
        return self.done()
