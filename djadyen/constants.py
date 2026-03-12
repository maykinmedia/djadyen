from djadyen.choices import AdyenComponentSupport, Status

LIVE_URL_PREFIX_ERROR = "Please provide the live_url_prefix. "
"https://docs.adyen.com/development-resources/live-endpoints#live-url-prefix"

"""
If an adyen name is supported or not by the web components.
"""
ADYEN_WEB_COMPONENTS_SUPPORT = {
    "alipay": AdyenComponentSupport.Supported,
    "bankTransfer_IBAN": AdyenComponentSupport.Supported,  # SEPA Bank Transfer
    "bcmc": AdyenComponentSupport.Supported,  # Bancontact card
    "directEbanking": AdyenComponentSupport.Unsupported,  # Online bank transfer - only API # noqa: E501
    "ebanking_FI": AdyenComponentSupport.Supported,  # Finnish E-Banking
    "ideal": AdyenComponentSupport.Supported,
    "scheme": AdyenComponentSupport.Supported,  # Credit/Debit cards
    "sepadirectdebit": AdyenComponentSupport.Supported,  # SEPA Direct Debit
}

"""
'These result codes indicate that the payment has reached a final state.'
https://docs.adyen.com/online-payments/build-your-integration/payment-result-codes#final-payment-status
"""
ADYEN_FINAL_STATE_CODES = (
    Status.Authorised.value,
    Status.Cancel.value,
    Status.Error.value,
    Status.Refused.value,
)
