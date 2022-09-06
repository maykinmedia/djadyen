import logging

from django.http import JsonResponse, HttpResponseRedirect
from django.views.generic.detail import DetailView

import Adyen

from djadyen import settings
from djadyen.choices import Status

logger = logging.getLogger("adyen")


class AdyenPaymentView(DetailView):
    """
    A view which initiates the Adyen payment by rendering a widget.
    It will automatically draw the wanted widget.
    """

    template_name = "adyen/pay.html"
    slug_field = "reference"
    slug_url_kwarg = "reference"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.get_price_in_cents() == 0:
            return HttpResponseRedirect(self.object.get_return_url())
        return super(AdyenPaymentView, self).get(request, *args, **kwargs)


class AdyenResponseView(DetailView):
    slug_field = "reference"
    slug_url_kwarg = "reference"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.get_price_in_cents() == 0:
            self.handle_authorised(self.object)

        resultRedirect = request.GET.get("redirectResult")
        if resultRedirect:
            ady = Adyen.Adyen()
            # Setting global values
            ady.payment.client.platform = settings.DJADYEN_ENVIRONMENT
            ady.payment.client.xapikey = settings.DJADYEN_SERVER_KEY
            ady.payment.client.app_name = settings.DJADYEN_APPNAME
            # Setting request data.
            request = {
                "details": {
                    "redirectResult": resultRedirect,
                },
            }
            # Requesting the status.
            result = ady.checkout.payments_details(request)
            if result.message.get("resultCode") == "Authorised":
                self.handle_authorised(self.object)
        return super(AdyenResponseView, self).get(request, *args, **kwargs)

    def handle_authorised(self, order):
        raise NotImplementedError()


class AdyenOrderStatusView(DetailView):
    slug_field = "reference"
    slug_url_kwarg = "reference"

    def get(self, request, *args, **kwargs):
        order = self.get_object()
        updated_status = True
        if order.status in [Status.Created, Status.Pending]:
            updated_status = False

        return JsonResponse(
            {
                "updatedStatus": updated_status,
                "currentStatus": order.status,
                "reference": order.reference,
            }
        )
