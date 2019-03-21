import logging

from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin

from djadyen import settings

from .choices import Status
from .forms import PaymentForm
from .hpp import HPPPaymenRequest, HPPPaymentResponse, sign_params

try:
    from urllib.parse import urlencode
except Exception:
    from urllib import urlencode


logger = logging.getLogger('adyen')


class AdyenRedirectView(SingleObjectMixin, FormView):
    """
    A view which initiates the Adyen payment by redirecting the user to Adyen.

    This view renders a form with the form-data which Adyen accepts, which points
    to an URL which Adyen accepts.

    For testing purposes you can set 'ADYEN_ENABLED' to False, which instead of
    posting the data to Adyen, posts the data to this view, which then processes
    it in similar fashion as Adyen.
    """

    template_name = 'adyen/form.html'
    form_class = PaymentForm
    slug_field = 'reference'
    slug_url_kwarg = 'reference'

    def get_form_kwargs(self):
        kwargs = super(AdyenRedirectView, self).get_form_kwargs()
        kwargs.update({
            "initial": self.payment_request.get_adyen_params()
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(AdyenRedirectView, self).get_context_data(**kwargs)
        if settings.ADYEN_ENABLED:
            context.update({
                'adyen_url': self.payment_request.get_adyen_url(),
                'add_csrf': False
            })
        else:
            context.update({
                'adyen_url': self.get_current_url(),
                'add_csrf': True
            })
        return context

    def get_payment_request(self, obj):
        return HPPPaymenRequest.from_object(obj, self.get_next_url())

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.payment_request = self.get_payment_request(self.object)

        if self.can_skip_payment():
            return self.skip_payment()

        response = super(AdyenRedirectView, self).get(request, *args, **kwargs)
        self.perform_action()
        return response

    def can_skip_payment(self):
        """
        A function to determain if we should skip the payment redirect
        """
        return False

    def skip_payment(self):
        raise NotImplementedError("You can't skip payments yet")

    def post(self, request, *args, **kwargs):
        """
        Normaly this post will go to Adyen. But for local development and intergrated testing this
        function can be used so no user action is required to test the handling.
        """
        if settings.ADYEN_ENABLED:
            raise Http404("Cannot handle post when adyen is enabled")

        order = self.get_object()
        params = {
            "authResult": settings.ADYEN_NEXT_STATUS,
            "pspReference": "Local redirect",
            "merchantReference": order.reference,
            "skinCode": settings.ADYEN_SKIN_CODE,
            "paymentMethod": "ideal",
            "shopperLocale": "NL",
        }

        signed_params = sign_params(params)
        return HttpResponseRedirect("{}?{}".format(self.get_next_url(), urlencode(signed_params)))

    def perform_action(self):
        pass

    def get_next_url(self):
        raise NotImplementedError

    def get_current_url(self):
        return "."


class AdyenResponseMixin(object):
    def post(self, request, *args, **kwargs):
        request.GET = request.POST
        return self.get(request, *args, **kwargs)

    def done(self):
        self.order.save()

        return self.render_to_response(self.get_context_data())

    def get(self, request, *args, **kwargs):
        self.payment_response = HPPPaymentResponse.from_data(request.GET)

        # If 'merchant_reference' is not set in the response (would be None in the object)
        # and we would query with this, get_object_or_404 would do a query on _everything_
        # in the database.
        #
        # I would prefer to do a proper sanitizing step in the class. But I'm refactoring a
        # lot already.
        #
        if self.payment_response.merchant_reference is None:
            raise Http404

        try:
            self.order = get_object_or_404(
                self.model, reference=self.payment_response.merchant_reference
            )
        except Exception:
            raise Http404

        #
        # This is a very important step, otherwise payments can be processed twice. By re-using
        # the URL.
        #
        if self.order.status != Status.Created:
            raise Http404

        if not self.payment_response.is_valid():
            calculated_params = self.payment_response.get_adyen_params()
            logger.debug('Order ref: %s | MerchangeSig not correct', self.payment_response.merchant_reference)
            logger.debug(
                'Order ref: %s | Our Msig: %s | Adyen Msig: %s',
                self.payment_response.merchant_reference,
                calculated_params['merchantSig'],
                self.payment_response.merchant_sig
            )
            return self.handle_error()

        logger.info(
            'Order ref: %s | Received Adyen auth result: %s',
            self.payment_response.merchant_reference,
            self.payment_response.auth_result
        )

        self.handle_default()

        if self.payment_response.auth_result == 'ERROR':
            return self.handle_error()

        if self.payment_response.auth_result == 'CANCELLED':
            return self.handle_canceled()

        if self.payment_response.auth_result == 'REFUSED':
            return self.handle_refused()

        if self.payment_response.auth_result == 'PENDING':
            return self.handle_pending()

        if self.payment_response.auth_result == 'AUTHORISED':
            return self.handle_authorised()

        logger.error("Please implement the following authResult: %s", self.payment_response.auth_result)
        return self.handle_pending()

    def handle_authorised(self):
        raise NotImplementedError()

    def handle_pending(self):
        raise NotImplementedError()

    def handle_refused(self):
        raise NotImplementedError()

    def handle_error(self):
        raise NotImplementedError()

    def handle_canceled(self):
        raise NotImplementedError()

    def handle_default(self):
        return
