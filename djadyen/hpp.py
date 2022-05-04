import base64
import binascii
import hashlib
import hmac
import logging
from collections import OrderedDict
from datetime import timedelta

from django.utils import timezone

from djadyen import settings

logger = logging.getLogger('adyen')


def escape_val(val):
    try:
        return val.replace('\\', '\\\\').replace(':', '\\:')
    except AttributeError:
        return str(val)


def sign_params(params):
    """
    Description of how the HMAC can be calculated can be found here

    https://docs.adyen.com/developers/classic-integration/hosted-payment-pages/hmac-signature-calculation
    """
    hmac_key = binascii.a2b_hex(settings.ADYEN_MERCHANT_SECRET)

    params = OrderedDict(sorted(params.items(), key=lambda t: t[0]))
    logger.debug("Ordered Params: %s", params)

    signing_string = ':'.join(map(escape_val, list(params.keys()) + list(params.values())))
    logger.debug("Signing Params: %s", signing_string)

    hmac_string = hmac.new(hmac_key, signing_string.encode('utf-8'), hashlib.sha256)
    logger.debug("HMAC: %s", hmac_string)

    params['merchantSig'] = base64.b64encode(hmac_string.digest()).decode("utf-8")
    logger.debug("merchantSig: %s", params['merchantSig'])
    return params
