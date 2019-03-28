import base64
import binascii
import hashlib
import hmac
from collections import OrderedDict

from djadyen import settings


def escape_val(val):
    try:
        return val.replace('\\', '\\\\').replace(':', '\\:')
    except AttributeError:
        return str(val)


def create_hmac(data):
    """
    Description of how the HMAC can be calculated can be found here

    https://docs.adyen.com/developers/development-resources/notifications/signing-notifications-with-hmac
    """
    hmac_key = binascii.a2b_hex(settings.ADYEN_NOTIFICATION_SECRET)

    sign_fields = [
        'pspReference',
        'originalReference',
        'merchantAccountCode',
        'merchantReference',
        'value',
        'currency',
        'eventCode',
        'success'
    ]

    msg_params = OrderedDict(
        [(key, data.get(key, '')) for key in sign_fields]
    )
    hmac_input = ':'.join([escape_val(value) for key, value in msg_params.items()])
    hmac_value = hmac.new(hmac_key, hmac_input.encode('utf-8'), hashlib.sha256)
    return (
        base64.b64encode(hmac_value.digest()).decode("utf-8")
    )
