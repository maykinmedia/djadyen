# Changelog

# 4.2.2
- fix iDEAL using the wrong payment type for donation

# 4.2.1
- fix order in `handle_authorised` and `handle_error` payment views
- fix wrong coverage badge
- refactor session views to use pytest
- improve response & session view coverage

# 4.2.0
- handle "final state" payments, e.g. Authorised or Error, in the `/payment/details/` API
  - `AdyenPaymentDetailsAPI` now has `handle_error()` and must implement `handle_authorised()`
- add iDeal redirect for the advanced view to bypass the web component
- refactor `AdyenPaymentView` and `AdyenAdvancedPaymentView` to use common `CommonPaymentAdyenView`
  - `AdyenOrder.get_redirect_url()` will now warn if it's not implemented and
  return `get_return_url()` instead of raising an exception
- add `status_message` field to the Order model
- add `ADYEN_FINAL_STATE_CODES` constant for done payment statuses
- change the Djadyen statuses choices to match the Adyen format e.g. `authorised` -> `Authorised`
- fix donation `status_message` not being saved in the donation view
- remove `jshint` npm package
- replace individual `django_db` marks with pytestmark
- add the reports directory to .gitignore

# 4.1.2
- fix using the same idempotency key in APIs breaking the payment details endpoint
- handle adyen exceptions in the API views

# 4.1.1
- add missing functions and template from the donation view
- fix donation objects being able to update after the donation is pending
- fix the donation component breaking with the no or empty campaign
- update testapp Order and Donation object
- add advanced, donation, and status view tests
- add template tags tests


# 4.1.0
- add advance Adyen checkout
- add Adyen Giving donation component
- add more logging
- update add `get_locale` to adyen views
  - Now should overwrite `get_locale` instead of fixing in `get_context_data`
- update `Adyen-Web` to 6.31.0
- update `bump-my-version` config


# 4.0.0
- **BREAKING CHANGE:** Upgrade `Adyen-web` to v6
  - payment methods must now be explicitly added
  - now only supports: Alipay, Bancontact, debit/credit card, Finnish e-banking, iDEAL, SEPA bank transfer, SEPA direct debit
  - issues are now used for _brands_ in certain payment methods (Bancontact, Credit/Debit Card)
  - now uses locales instead of language codes, must be changed from a language code to use translated payments
- Add the ability to use a payment option language locale in `AdyenPaymentView`
- Update `adyen_payment_component` tag now uses language argument in `Adyen-web` javascript checkout
- Show issuer/brands in `AdyenPaymentOption` admin
- Show if `adyen_name` is supported in `AdyenPaymentOption` admin
- Switch to ruff for code quality
- Add django 5.2 and python 3.12 in CI tests

# 3.3.1
- Fix dependencies in `pyproject.toml`
- Switch `setup.cfg` to `pyproject.toml`
- Fix master branch not using in CI

# 3.3.0
-   Added support for custom Adyen styles via `DJADYEN_STYLES` Django setting
-   Removed `django-choices`
-   Replaces `bumpversion` with `bump-my-version`
-   Use `README.md` instead of not existing `README.rst` in `setup.cfg`

# 3.2.0
-   Update adyen-web to support iDeal 2.0

# 3.1.1
-   Deal with empty payment_option

# 3.1.0
-   Adding support for iDeal 2.0

# 3.0.0

-   Updated the Adyen to 10+.

# 2.0.4

-   Switched to Web Drop-in and Web Compoments instead of HPP pages

# 1.1.1

-   Fixed the processing of created orders by notifications.
-   Fixed that notifications older than `ADYEN_HANDLE_NOTIFICATION_MINUTES_AGO` minutes will be processed.

# 1.1.0

-   Removed the auto-fetch option.
-   Improved README documentation.
-   Refectored some core code to make it more reusable.
-   Validate the notification that is send.
-   Added a default management command to handle the notifications.

# 1.0.1

-   Fixed the bug where not all fields that were passed were created and send to adyen. Causing an error.

# 1.0.0

-   Created an initial release that supports Django 1.11, Django 2.0 and python 3.4+.
