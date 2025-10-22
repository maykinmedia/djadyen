# DjAdyen

[![PyPI version](https://badge.fury.io/py/djadyen.svg)](https://badge.fury.io/py/djadyen)
[![Testing](https://github.com/maykinmedia/djadyen/actions/workflows/main.yml/badge.svg)](https://github.com/maykinmedia/djadyen/actions/workflows/main.yml)
[![Linting](https://github.com/maykinmedia/djadyen/actions/workflows/linting.yml/badge.svg)](https://github.com/maykinmedia/djadyen/actions/workflows/linting.yml)

This module is used to connect your django application to the payment provider Adyen using the ["Web Components"](https://docs.adyen.com/online-payments/web-components) and ["Web Drop-in"](https://docs.adyen.com/online-payments/web-drop-in)

This is only tested on a postgres database.

## Supported Ayden Payments

- **Alipay** - adyen name: `alipay`
- **Bancontact** card - adyen name: `bcmc`, uses brands
- **(Debit/Credit) Card** - adyen name: `schema`, uses brands
- **Finnish E-Banking** - adyen name: `ebanking_FI`
- **iDEAL** - adyen name: `ideal`
- **SEPA Bank Transfer** - adyen name: `bankTransfer_IBAN`
- **SEPA Direct Debit** - adyen name: `sepadirectdebit`

### Issuers & Brands
Both issuers and brands are used for `AdyenIssuer` objects for different payment options.
Some will use one `adyen_id` for one issuer while some others will use a list of `adyen_id`s for allowed brands.


## Installation

Install with pip

```shell
pip install djadyen
```

Add _'djadyen'_ to the installed apps

```python
# settings.py

INSTALLED_APPS = [
    ...
    'djadyen',
    ...
]
```

Add the Adyen notifications urls (This is not required). These url will save all the notifications to the database. You need to make an implementation to handle the notifications

```python
# urls.py

urlpatterns = [
    ...
    url(r'^adyen/notifications/', include('djadyen.notifications.urls', namespace='adyen-notifications')),
    ...
]
```

```python
# models.py
from djadyen.models import AdyenOrder

class CustomOrder(AdyenOrder):
    def get_price_in_cents(self):
        """
        :return int Return the price in cents for this order.
        """
        raise NotImplementedError

    def get_return_url(self):
        raise NotImplementedError(
            "Please override 'get_return_url' on the '{model_name}'".format(
                model_name=self.\_meta.object_name
            )
        )

```

## Usage

### Management command

There is a management command that will sync the payment methods for you. This can be used if you want the users to select a payment method/issuer on your own site.

`manage.py sync_payment_methods`

There is a command that will call the function `process_notification` to handle notifications. This can be added to a crontab.

`manage.py adyen_maintenance`

### Required settings

-   `DJADYEN_SERVER_KEY` _This is the server key. This should be a secret string._
-   `DJADYEN_CLIENT_KEY` _This is the client key. This key will be used in the components in the frontend._
-   `DJADYEN_MERCHANT_ACCOUNT` _This is the merchant accont that is used in Adyen._
-   `DJADYEN_ORDER_MODELS` _A list of models that are used to store Orders (Inherit from AdyenOrder). The models should be strings in the <app_label>.<model_name> form_
-   `DJADYEN_NOTIFICATION_KEY` _The key to verify the notifications are from adyen_

### Optional settings

-   `DJADYEN_CURRENCYCODE` _(default='EUR') This can be set to any other currency Adyen supports._
-   `DJADYEN_ENVIRONMENT` _(default='test') This can be 'test' or 'live'._
-   `DJADYEN_APPNAME` _(default='Djadyen Payment') This is the name that will be send along with the payment._
-   `DJADYEN_REFETCH_OLD_STATUS` _(default=False) This is so you will always have the latest saved status. This will cause an extra db query!_
-   `DJADYEN_HANDLE_NOTIFICATION_MINUTES_AGO` _(default=15) This defaults to 15 minutes. You can change the value to make this shorter or longer depending on the need._

#### DJADYEN_STYLES

(Optional) Customize the appearance of Adyen payment components.

This setting allows you to configure the styling of Adyen Web Components by providing style definitions that are passed to the payment component configuration. This enables you to customize colors, fonts, and other visual properties of the payment form fields.

**Example:**
```python
# settings.py
DJADYEN_STYLES = {
    'base': {
        'color': '#000000',
        'fontSize': '16px',
        'fontFamily': 'Arial, sans-serif',
    },
    'placeholder': {
        'color': '#999999',
    },
    'error': {
        'color': '#ff0000',
    },
    'validated': {
        'color': '#00ff00',
    }
}
```

**How it works:**

The styles object is passed to the Adyen payment component configuration, allowing you to customize the appearance of input fields. The configuration supports several style categories:

-   `base`: Default styling for form input fields
-   `placeholder`: Styling for placeholder text
-   `error`: Styling for fields in an error state
-   `validated`: Styling for successfully validated fields

**Available style properties:**

Within each category, you can use properties like:
-   `color`: Text color
-   `fontSize`: Font size (e.g., '16px', '1rem')
-   `fontFamily`: Font family
-   `fontWeight`: Font weight
-   `lineHeight`: Line height
-   And other CSS-like properties supported by Adyen components

For a complete list of available styling options and examples, refer to the [Adyen Card Component Styling Documentation](https://docs.adyen.com/payment-methods/cards/custom-card-integration/#styling).

**Note:** These styles apply specifically to Adyen's secured fields (like card number, CVV, expiry date). For styling the container or other elements, use regular CSS in your stylesheets.

If `DJADYEN_STYLES` is not set, Adyen's default styling will be used.

### Order object

There is an abstract order in this package. This will save you some time on creating an order for adyen.
There are some features on the order that will make it easier to integrate your order with this package.

The added fields are:

-   `status` _This is the status of the object. This will be changed by adyen._
-   `created_at` _This field is used for when the order is created._
-   `reference` _This field is a communication field. It is not used outside the communication. This will be set by uuid4, but can be overwritten._
-   `psp_reference` _This field is the reference from Adyen. With this field you are able to search in the Adyen inderface._
-   `payment_option` _This is the Adyen payment option from this package._
-   `issuer` _This is the Adyen issuer from this package._

You should implement the following methods

-   `get_price_in_cents` _Return the price to be paid for this order_
-   `process_authorized_notification` _Process a 'authorized' notification which adyen has sent_
-   `process_notification` _Process the notification, if you are using the adyen-maintenance management command_

### AdyenPaymentView

This view is used to show the payment page.

This page can be customized in 2 ways.

1. overwrite the template (`adyen/pay,html`)
2. Overwrite the view and changing the `template_name`

```python
from djadyen.views import AdyenPaymentView


class PaymentView(AdyenPaymentView):
    template_name = "my_adyen/pay.html"  # Optional
```

Adyen requires a language locale i.e. `nl-NL` or `en-US` instead of `nl` or `en`.
If Django's uses language codes, `adyen_language` should be converted in the view context similarly to this:

```python
ADYEN_LANGUAGES = {
    "nl": "nl-NL",
    "en": "en-US",
}

class PaymentView(AdyenPaymentView):
    ...
    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {"adyen_language": ADYEN_LANGUAGES[self.request.LANGUAGE_CODE]}

```


### AdyenResponseView

Adyen also creates a response. This will help you with catching the response. This view will check if
the response from Adyen is valid. It will also provide some usefull functions so you don't have to overwrite anything.

In this example the order is automaticly fetched from the reference that is passed in the merchantReference.
It will also set the order in the self object for easy access. In the done function the order is saved
and the template will be rendered.

```python
from djadyen.views import AdyenResponseView
from djadyen.choices import Status


class ConfirmationView(AdyenResponseView, TemplateView):
    template_name = 'my_project/confirmation.html'
    model = Order

    def handle_authorised(self):
        self.order.status = Status.Authorised
        return self.done()
```

# Adyen notifications

Setup the standard notifications in Adyen. These will comunicate about the payments if they were succesful or not.
This is **very important** because the notifications will be needed when a payment is redirected with a pending payment.

The notifications will be stored in the database. You need to write the handling of the notifications yourself or use the `adyen_maintenance` command.

## License

[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fmaykinmedia%2Fdjadyen.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Fmaykinmedia%2Fdjadyen?ref=badge_large)
