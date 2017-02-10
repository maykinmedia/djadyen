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

        if initial.get('shopperEmail'):
            self.fields['shopperEmail'] = forms.CharField()
        if initial.get('shipBeforeDate'):
            self.fields['shipBeforeDate'] = forms.CharField()
        if initial.get('merchantReturnData'):
            self.fields['merchantReturnData'] = forms.CharField()
        if initial.get('resURL'):
            self.fields['resURL'] = forms.CharField()
        if initial.get('brandCode'):
            self.fields['brandCode'] = forms.CharField()
        if initial.get('issuerId'):
            self.fields['issuerId'] = forms.CharField()
