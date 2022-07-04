import logging

from django.http import Http404
from django.views.generic.detail import DetailView

import Adyen

from djadyen import settings

from .choices import Status

logger = logging.getLogger("adyen")


class AdyenPaymentView(DetailView):
    """
    A view which initiates the Adyen payment by rendering a widget.
    It will automatically draw the wanted widget.
    """

    template_name = "adyen/pay.html"
    slug_field = "reference"
    slug_url_kwarg = "reference"


class AdyenResponseView(DetailView):
    slug_field = "reference"
    slug_url_kwarg = "reference"

    def done(self):
        self.order.save()

        return self.render_to_response(self.get_context_data())

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.order = self.object
        redirect_result = request.GET.get("redirectResult")
        if redirect_result is None:
            raise Http404

        ady = Adyen.Adyen()

        # Setting global values
        ady.payment.client.platform = settings.DJADYEN_ENVIRONMENT
        ady.payment.client.xapikey = settings.DJADYEN_SERVER_KEY
        ady.payment.client.app_name = settings.DJADYEN_APPNAME

        response = ady.checkout.payments_details({"details": {"redirectResult": redirect_result}})
        auth_result = response.message.get("resultCode")
        self.order.psp_reference = response.psp

        #
        # This is a very important step, otherwise payments can be processed twice.
        # By re-using the URL.
        #
        if self.order.status != Status.Created:
            raise Http404

        logger.info(
            "Order ref: %s | Received Adyen auth result: %s",
            self.order.reference,
            auth_result,
        )

        self.handle_default()
        if auth_result == "Error":
            return self.handle_error()

        if auth_result == "Cancelled":
            return self.handle_canceled()

        if auth_result == "Refused":
            return self.handle_refused()

        if auth_result in ["Pending", "PresentToShopper", "Received"]:
            return self.handle_pending()

        if auth_result == "Authorised":
            return self.handle_authorised()

        logger.error("Please implement the following authResult: %s", auth_result)
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
