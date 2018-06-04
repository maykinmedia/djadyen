from django import forms

from djadyen import settings


class PaymentForm(forms.Form):
    skinCode = forms.CharField(initial=settings.ADYEN_SKIN_CODE)
    currencyCode = forms.CharField(initial=settings.ADYEN_CURRENCYCODE)
    merchantAccount = forms.CharField(initial=settings.ADYEN_MERCHANT_ACCOUNT)

    sessionValidity = forms.CharField()
    merchantReference = forms.CharField()
    paymentAmount = forms.CharField()

    merchantSig = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)

        initial = kwargs.get('initial')

        fixed_fields = [
            'skinCode', 'currencyCode', 'merchantAccount', 'sessionValidity', 'merchantReference',
            'paymentAmount', 'merchantSig'
        ]

        for key, value in initial.items():
            if key not in fixed_fields:
                self.fields[key] = forms.CharField(initial=value)
