import json
import logging

try:
    # python 3.13+
    from warnings import deprecated
except ImportError:
    from typing_extensions import deprecated

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.views.generic.detail import DetailView

import Adyen
from Adyen.exceptions import AdyenAPIResponseError
from glom import PathAccessError, glom

from djadyen.choices import Status
from djadyen.constants import LIVE_URL_PREFIX_ERROR
from djadyen.models import AdyenDonation
from djadyen.settings import get_setting
from djadyen.utils import setup_adyen_client

logger = logging.getLogger("adyen")


class AdyenDetailView(DetailView):
    """
    Generic Adyen Order Detail view
    """

    slug_field = "reference"
    slug_url_kwarg = "reference"


class CommonAdyenPaymentView(AdyenDetailView):
    """
    Common functionality for Adyen checkout and payments
    """

    def get_locale(self) -> str:
        """
        Get the Adyen locale. By default, takes the request language code.
        Adyen expects a full locale e.e en-US
        """
        return self.request.LANGUAGE_CODE

    def redirect_ideal_2(self, request):
        logger.info("Start new payment for  %s", self.object.reference)
        ady = setup_adyen_client()

        body = {
            "amount": {
                "value": self.object.get_price_in_cents(),
                "currency": get_setting("DJADYEN_CURRENCYCODE"),
            },
            "paymentMethod": {"type": "ideal"},
            "reference": str(self.object.reference),
            "merchantAccount": get_setting("DJADYEN_MERCHANT_ACCOUNT"),
            "returnUrl": self.object.get_redirect_url(),
            "shopperLocale": self.get_locale(),
            "countryCode": (get_setting("DJADYEN_DEFAULT_COUNTRY_CODE").lower()),
        }

        try:
            request["shopperEmail"] = self.object.email
        except Exception:
            pass

        result = ady.checkout.payments_api.payments(
            body, idempotency_key=self.object.reference
        )
        logger.info(request)

        if result.status_code == 200:
            if redirect_url := glom(
                result.message, "action.url", skip_exc=PathAccessError
            ):
                return redirect(redirect_url)

        return redirect(self.object.get_return_url())

    def get_context_data(self, **kwargs) -> dict[str, any]:
        # needs to use adyen web supported language codes e.g. en-US, nl-NL
        return super().get_context_data(**kwargs) | {
            "adyen_language": self.get_locale(),
        }


class AdyenSessionPaymentView(CommonAdyenPaymentView):
    """
    A view which initiates the Adyen payment by rendering a widget.
    It will automatically draw the wanted widget.
    """

    template_name = "adyen/pay.html"

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
        return super().get(request, *args, **kwargs)


@deprecated(
    "Renamed to `AdyenSessionPaymentView` to differentiate "
    "from the Advanced payment view."
)
class AdyenPaymentView(AdyenSessionPaymentView): ...


class AdyenResponseView(AdyenDetailView):
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.get_price_in_cents() == 0:
            self.handle_authorised()

        resultRedirect = request.GET.get("redirectResult")
        if resultRedirect:
            ady = Adyen.Adyen()

            if not get_setting("DJADYEN_ENVIRONMENT"):
                raise ImproperlyConfigured("Please provide an environment.")

            if get_setting("DJADYEN_ENVIRONMENT") == "live" and not get_setting(
                "DJADYEN_LIVE_URL_PREFIX"
            ):
                raise ImproperlyConfigured(LIVE_URL_PREFIX_ERROR)

            # Setting global values
            ady.payment.client.platform = get_setting("DJADYEN_ENVIRONMENT")
            ady.payment.client.xapikey = get_setting("DJADYEN_SERVER_KEY")
            ady.payment.client.app_name = get_setting("DJADYEN_APPNAME")
            ady.payment.client.live_endpoint_prefix = get_setting(
                "DJADYEN_LIVE_URL_PREFIX"
            )

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
                self.handle_authorised()
            elif result_code != "Pending":
                self.handle_error()
        return super().get(request, *args, **kwargs)

    def handle_authorised(self) -> None:
        """
        Handle what happens to a order after a payment is authorised
        e.g change order to status and send confirmation email
        """
        raise NotImplementedError(
            "Handle what happens to a order after a payment is authorised. "
            "Use self.object"
        )

    def handle_error(self):
        self.object.status = Status.Error
        self.object.save()


class AdyenStatusView(DetailView):
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


@deprecated("Renamed to `AdyenStatusView` as it supports both orders and donations.")
class AdyenOrderStatusView(AdyenStatusView): ...


class AdyenAdvancedPaymentView(CommonAdyenPaymentView):
    template_name = "adyen/advanced_pay.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.get_price_in_cents() == 0:
            return HttpResponseRedirect(self.object.get_return_url())

        # Ideal 2.0 flow, ideal sorts out the bank itself.
        # Skip if redirectResult is present, as it means the payment is already done
        # and can cause loops.
        if (
            not request.GET.get("redirectResult")
            and self.object.payment_option
            and self.object.payment_option.adyen_name == "ideal"
            and not self.object.issuer
        ):
            return self.redirect_ideal_2(request)

        return super().get(request, *args, **kwargs)


class AdyenDonationView(CommonAdyenPaymentView):
    """
    Allows dontaiton option after finishing the original payment.
    Should be done
    """

    template_name = "adyen/donation.html"

    def get_donation(self):
        ady = setup_adyen_client()
        json_request = {
            "merchantAccount": get_setting("DJADYEN_MERCHANT_ACCOUNT"),
            "currency": get_setting("DJADYEN_CURRENCYCODE"),
            "locale": self.get_locale(),
        }

        result = ady.checkout.donations_api.donation_campaigns(request=json_request)
        if result.status_code == 200 and result.message.get("donationCampaigns"):
            return result.message.get("donationCampaigns")[0]
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.get_donation()
        context["redirect_url"] = self.get_redirect_url()
        return context

    def get_redirect_url(self) -> str:
        """
        Where to redirect after closing the donation component
        :return: URL
        """
        return "/"

    def get_donation_model(self) -> AdyenDonation:
        raise NotImplementedError("Donation model is required to create a donation")

    def get_donation_confirmation_url(self) -> str:
        raise NotImplementedError(
            "Donation confirmation url is required to redirect to after donation"
        )

    def handle_authorised(self) -> None:
        """
        Handle what happens to a order after a payment is authorised
        e.g change order to status and send confirmation email
        """
        raise NotImplementedError(
            "Handle what happens to a order after a payment is authorised. "
            "Use self.object"
        )

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        # handle free payment
        if self.object.get_price_in_cents() == 0:
            self.handle_authorised()

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        ady = setup_adyen_client()

        amount = json.loads(request.POST["amount"])
        amount_value = amount["value"]
        campaign_id = request.POST["donation_campaign_id"]

        logger.info("Start new donation payment for  %s", self.object.reference)

        Donation = self.get_donation_model()
        donation, created = Donation.objects.get_or_create(
            order=self.object,
            defaults={"amount": amount_value, "campaign": campaign_id},
        )

        # if the donation API is not sent yet
        if donation.status == Status.Created.value:
            # if donation is created but not run, donation can be overrided
            if not created:
                donation.amount = amount_value
                donation.campaign = campaign_id

            try:
                # iDeal is sepadirectdebit
                # other current supported payment methods are scheme
                payemnt_type: str = (
                    "sepadirectdebit"
                    if self.object.payment_option.adyen_name == "ideal"
                    else "scheme"
                )

                donation_request = {
                    "amount": amount,
                    "donationCampaignId": campaign_id,
                    "paymentMethod": {"type": payemnt_type},
                    "donationOriginalPspReference": self.object.psp_reference,
                    "donationToken": self.object.donation_token,
                    "reference": str(donation.reference),
                    "merchantAccount": get_setting("DJADYEN_MERCHANT_ACCOUNT"),
                }
                result = ady.checkout.donations_api.donations(
                    donation_request, idempotency_key=str(donation.reference)
                )

            except AdyenAPIResponseError as e:
                logger.error(
                    "Error when creating donaiton %s: %s", donation.reference, e
                )
                donation.status_message = str(e)
                donation.status = Status.Error.value
                donation.save()
            else:
                logger.info("Donation created %s", donation.reference)
                if result.message["status"] == "refused":
                    donation.status = Status.Refused.value
                else:
                    donation.status = Status.Pending.value

                # TODO: better status message?
                donation.status_message = result.message
                donation.save()

        return redirect(self.get_donation_confirmation_url())
