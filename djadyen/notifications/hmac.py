import base64
import binascii
import hashlib
import hmac
import logging

from djadyen import settings

logger = logging.getLogger("adyen")


def get_signature(params):
    """
    Description of how the HMAC can be signed can be found here

    https://docs.adyen.com/development-resources/webhooks/verify-hmac-signatures
    """
    hmac_key = binascii.a2b_hex(settings.DJADYEN_NOTIFICATION_KEY)

    logger.debug("Params: %s", params)

    signing_string = "{part1}:{part2}".format(
        part1="{psp_reference}:{original_reference}:{merchant_account_code}".format(
            psp_reference=params.get("pspReference", ""),
            original_reference=params.get("originalReference", ""),
            merchant_account_code=params.get("merchantAccountCode", ""),
        ),
        part2="{merchant_reference}:{value}:{currency}:{event_code}:{success}".format(
            merchant_reference=params.get("merchantReference", ""),
            value=params.get("amount", {}).get("value", ""),
            currency=params.get("amount", {}).get("currency", ""),
            event_code=params.get("eventCode", ""),
            success=params.get("success", ""),
        ),
    )
    print(signing_string)
    logger.debug("Signing Params: %s", signing_string)

    hmac_string = hmac.new(hmac_key, signing_string.encode("utf-8"), hashlib.sha256)
    logger.debug("HMAC: %s", hmac_string)

    signature = base64.b64encode(hmac_string.digest()).decode("utf-8")
    logger.debug("signature: %s", signature)
    return signature
