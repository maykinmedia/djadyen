import json
import logging

from django.http import JsonResponse
from django.views import View
from django.views.generic.detail import SingleObjectMixin

from Adyen.exceptions import AdyenAPIResponseError

from djadyen import settings
from djadyen.choices import Status
from djadyen.models import AdyenOrder
from djadyen.utils import setup_adyen_client

logger = logging.getLogger("adyen")


def handle_adyen_error_response(
    api_name: str, obj: AdyenOrder, exception: AdyenAPIResponseError
) -> None:
    if exception.psp:
        obj.psp_reference = exception.psp

    if obj.status != Status.Authorised:
        obj.status = Status.Error
    obj.status_message = f"Adyen API {api_name} - {exception}"
    obj.save()


class AdyenPaymentsAPI(SingleObjectMixin, View):
    slug_field = "reference"
    slug_url_kwarg = "reference"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "bad response"}, status=400)

        payment_method = data.get("paymentMethod")

        if not payment_method:
            return JsonResponse({"error": "bad response"}, status=400)
        json_request = {
            "amount": {
                "currency": "EUR",
                "value": self.object.get_price_in_cents(),
            },
            "reference": str(self.object.reference),
            "paymentMethod": payment_method,
            "returnUrl": self.object.get_redirect_url(),
            "merchantAccount": settings.DJADYEN_MERCHANT_ACCOUNT,
        }

        if data.get("riskData"):
            json_request["riskData"] = data["riskData"]

        if data.get("checkoutAttemptId"):
            json_request["checkoutAttemptId"] = data["checkoutAttemptId"]

        # Send the request
        logger.info("Start new payment for  %s", self.object.reference)
        adyen_client = setup_adyen_client()

        try:
            result = adyen_client.checkout.payments_api.payments(
                request=json_request,
                idempotency_key=f"{self.object.reference}-payments",
            )
        except AdyenAPIResponseError as e:
            handle_adyen_error_response("/payments/", self.object, e)
            return JsonResponse({"error": "bad response"}, status=400)

        # only return what checkout wants from payments
        response = {
            "resultCode": result.message["resultCode"],
            "action": result.message.get("action"),
            "order": result.message.get("order"),
            "donationToken": result.message.get("donationToken"),
        }

        self.object.status = Status.Pending.value
        self.object.psp_reference = result.message.get("pspReference", "")

        if response["donationToken"]:
            self.object.donation_token = response["donationToken"]
        self.object.save()

        return JsonResponse(response, status=200)


class AdyenPaymentDetailsAPI(SingleObjectMixin, View):
    slug_field = "reference"
    slug_url_kwarg = "reference"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "bad response"}, status=400)

        if not data:
            return JsonResponse({"error": "bad response"}, status=400)

        # STATE_DATA is an object passed from your client app,
        # deserialized from JSON to a data structure.

        logger.info("Sending payment details for  %s", self.object.reference)
        adyen_client = setup_adyen_client()

        # Setting request data. For now assumes
        request = {
            "details": data,
        }
        try:
            result = adyen_client.checkout.payments_api.payments_details(
                request, idempotency_key=f"{self.object.reference}-detail"
            )
        except AdyenAPIResponseError as e:
            handle_adyen_error_response("/payment/details/", self.object, e)
            return JsonResponse({"error": "bad response"}, status=400)

        # only return what checkout wants from payment details
        response = {
            "resultCode": result.message["resultCode"],
            "action": result.message.get("action"),
            "order": result.message.get("order"),
            "donationToken": result.message.get("donationToken"),
        }

        self.object.status = Status.Pending.value
        if result.message.get("pspReference"):
            self.object.psp_reference = result.message["pspReference"]

        if response["donationToken"]:
            self.object.donation_token = response["donationToken"]
        self.object.save()

        return JsonResponse(response)
