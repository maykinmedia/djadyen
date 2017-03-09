import base64
import binascii
import hashlib
import hmac
import logging
from collections import OrderedDict
from datetime import datetime, timedelta

from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin

from djadyen import settings

from .forms import PaymentForm

try:
    from urllib.parse import urlencode
except Exception:
    from urllib import urlencode


logger = logging.getLogger('adyen')


class AdyenSigMixin(object):
    hmac_key = binascii.a2b_hex(settings.ADYEN_MERCHANT_SECRET)

    def escape_val(self, val):
        try:
            return val.replace('\\', '\\\\').replace(':', '\\:')
        except AttributeError:
            return str(val)

    def sign_params(self, parms):
        logger.debug("Params: %s", parms)

        parms = OrderedDict(sorted(parms.items(), key=lambda t: t[0]))
        logger.debug("Ordered Params: %s", parms)

        signing_string = ':'.join(map(self.escape_val, list(parms.keys()) + list(parms.values())))
        logger.debug("Signing Params: %s", signing_string)

        hmac_string = hmac.new(self.hmac_key, signing_string.encode('utf-8'), hashlib.sha256)
        logger.debug("HMAC: %s", hmac_string)

        parms['merchantSig'] = base64.b64encode(hmac_string.digest()).decode("utf-8")
        logger.debug("merchantSig: %s", parms['merchantSig'])

        return parms


class AdyenRequestMixin(AdyenSigMixin):
    def adyen_url(self, brand_code=None, issuer_id=None):
        page = 'hpp/select.shtml'
        if brand_code:
            page = 'hpp/details.shtml'
        if issuer_id:
            page = 'hpp/skipDetails.shtml'
        url = '{}{}'.format(settings.ADYEN_URL, page)

        logger.debug("Adyen Url: %s", url)
        return url


class AdyenRedirectView(AdyenRequestMixin, SingleObjectMixin, FormView):
    template_name = 'adyen/form.html'
    form_class = PaymentForm
    slug_field = 'reference'
    slug_url_kwarg = 'reference'

    default_params = {
        'skinCode': settings.ADYEN_SKIN_CODE,
        'currencyCode': settings.ADYEN_CURRENCYCODE,
        'merchantAccount': settings.ADYEN_MERCHANT_ACCOUNT,
    }

    def get_signed_order_params(self, order, **kwargs):
        params = self.get_default_params(
            merchantReference=order.reference,
            paymentAmount=order.get_price_in_cents(),
            resURL='{}{}'.format(settings.ADYEN_HOST_URL, self.get_next_url())
        )
        if order.email:
            params['shopperEmail'] = order.email
        if order.payment_option:
            params['brandCode'] = order.payment_option.adyen_name
        if order.issuer:
            params['issuerId'] = order.issuer.adyen_id

        params.update(**kwargs)

        return self.sign_params(params)

    def get_default_params(self, **kwargs):
        params = self.default_params.copy()
        valid = datetime.now() + timedelta(minutes=settings.ADYEN_SESSION_MINUTES)
        params.update(
            sessionValidity=valid.isoformat(),
        )
        params.update(**kwargs)
        return params

    def get_context_data(self, **kwargs):
        context = super(AdyenRedirectView, self).get_context_data(**kwargs)
        if settings.ADYEN_ENABLED:
            brand_code = None
            issuer_id = None
            if hasattr(self.object, "payment_option") and self.object.payment_option:
                brand_code = self.object.payment_option
            if hasattr(self.object, "issuer") and self.object.issuer:
                issuer_id = self.object.issuer.id
            context.update({
                'adyen_url': self.adyen_url(brand_code=brand_code, issuer_id=issuer_id),
                'add_csrf': False
            })
        else:
            context.update({
                'adyen_url': self.get_current_url(),
                'add_csrf': True
            })
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

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
            "merchantReference": order.reference
        }

        return HttpResponseRedirect("{}?{}".format(self.get_next_url(), urlencode(params)))

    def perform_action(self):
        pass

    def get_next_url(self):
        pass

    def get_current_url(self):
        return "."


class AdyenResponseMixin(AdyenSigMixin):
    auto_fetch = True

    def post(self, request, *args, **kwargs):
        request.GET = request.POST
        return self.get(request, *args, **kwargs)

    def done(self):
        if self.auto_fetch:
            self.order.save()

        return self.render_to_response(self.get_context_data())

    def get(self, request, *args, **kwargs):
        self.auth_result = request.GET.get('authResult')
        self.psp_reference = request.GET.get('pspReference')
        self.merchant_reference = request.GET.get('merchantReference')
        self.skin_code = request.GET.get('skinCode')
        self.payment_method = request.GET.get('paymentMethod')
        self.shopper_locale = request.GET.get('shopperLocale')
        self.merchant_return_data = request.GET.get('merchantReturnData')
        self.reason = request.GET.get('reason')

        self.merchant_sig = request.GET.get('merchantSig')

        params = {
            'authResult': self.auth_result,
            'merchantReference': self.merchant_reference,
            'skinCode': self.skin_code,
            'paymentMethod': self.payment_method,
            'shopperLocale': self.shopper_locale,
        }

        if self.psp_reference:
            params['pspReference'] = self.psp_reference
        if self.merchant_return_data:
            params['merchantReturnData'] = self.merchant_return_data
        if self.reason:
            params['reason'] = self.reason

        sig = self.sign_params(params)

        if self.auto_fetch:
            try:
                self.order = get_object_or_404(self.model, reference=self.merchant_reference)
            except Exception:
                raise Http404

        self.handle_default()
        logger.info(
            'Order ref: %s | Received Adyen auth result: %s',
            self.merchant_reference,
            self.auth_result
        )

        if sig['merchantSig'] != self.merchant_sig:
            logger.debug('Order ref: %s | MerchangeSig not correct', self.merchant_reference)
            logger.debug(
                'Order ref: %s | Our Msig: %s | Adyen Msig: %s',
                self.merchant_reference,
                sig['merchantSig'],
                self.merchant_sig
            )
            return self.handle_error()

        if self.auth_result == 'ERROR':
            return self.handle_error()

        if self.auth_result == 'CANCELLED':
            return self.handle_canceled()

        if self.auth_result == 'REFUSED':
            return self.handle_refused()

        if self.auth_result == 'PENDING':
            return self.handle_pending()

        if self.auth_result == 'AUTHORISED':
            return self.handle_authorised()

        logger.error("Please implement the following authResult: %s", self.auth_result)
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
