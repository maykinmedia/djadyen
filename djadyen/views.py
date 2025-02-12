import logging

from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.views.generic.detail import DetailView

import Adyen
from glom import PathAccessError, glom

from djadyen import settings
from djadyen.choices import Status
from djadyen.constants import LIVE_URL_PREFIX_ERROR
from djadyen.utils import setup_adyen_client

logger = logging.getLogger("adyen")


class AdyenPaymentView(DetailView):
    """
    A view which initiates the Adyen payment by rendering a widget.
    It will automatically draw the wanted widget.
    """

    template_name = "adyen/pay.html"
    slug_field = "reference"
    slug_url_kwarg = "reference"

    def redirect_ideal_2(self, request):
        logger.info("Start new payment for {}".format(str(self.object.reference)))
        ady = setup_adyen_client()

        body = {
            "amount": {
                "value": self.object.get_price_in_cents(),
                "currency": settings.DJADYEN_CURRENCYCODE,
            },
            "paymentMethod": {"type": "ideal"},
            "reference": str(self.object.reference),
            "merchantAccount": settings.DJADYEN_MERCHANT_ACCOUNT,
            "returnUrl": self.object.get_return_url(),
            "shopperLocale": request.LANGUAGE_CODE.lower(),
            "countryCode": (settings.DJADYEN_DEFAULT_COUNTRY_CODE.lower()),
        }

        try:
            request["shopperEmail"] = self.object.email
        except Exception:
            pass

        result = ady.checkout.payments_api.payments(body)
        logger.info(request)

        if result.status_code == 200:
            if redirect_url := glom(
                result.message, "action.url", skip_exc=PathAccessError
            ):
                return redirect(redirect_url)

        return redirect(self.object.get_return_url())

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.get_price_in_cents() == 0:
            return HttpResponseRedirect(self.object.get_return_url())

        # Ideal 2.0 flow, ideal sorts out the bank itself.
        if (
            self.object.payment_option
            and self.object.payment_option.adyen_name == "ideal"
            and not self.object.issuer
        ):
            return self.redirect_ideal_2(request)
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

            if not settings.DJADYEN_ENVIRONMENT:
                assert False, "Please provide an environment."

            if (
                settings.DJADYEN_ENVIRONMENT == "live"
                and not settings.DJADYEN_LIVE_URL_PREFIX
            ):
                assert False, LIVE_URL_PREFIX_ERROR

            # Setting global values
            ady.payment.client.platform = settings.DJADYEN_ENVIRONMENT
            ady.payment.client.xapikey = settings.DJADYEN_SERVER_KEY
            ady.payment.client.app_name = settings.DJADYEN_APPNAME
            ady.payment.client.live_endpoint_prefix = settings.DJADYEN_LIVE_URL_PREFIX

            # Setting request data.
            request = {
                "details": {
                    "redirectResult": resultRedirect,
                },
            }
            # Requesting the status.
            result = ady.checkout.payments_api.payments_details(request)
            result_code = result.message.get("resultCode")
            if result_code == "Authorised":
                self.handle_authorised(self.object)
            elif result_code != "Pending":
                self.handle_error(self.object)
        return super(AdyenResponseView, self).get(request, *args, **kwargs)

    def handle_authorised(self, order):
        raise NotImplementedError()

    def handle_error(self, order):
        order.status = Status.Error
        order.save()


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
