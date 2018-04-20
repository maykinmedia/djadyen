from django.utils.translation import ugettext_lazy as _

from djchoices import ChoiceItem, DjangoChoices


class Status(DjangoChoices):
    Authorised = ChoiceItem('authorised', _('Authorised'))  # The payment is completed.
    Cancel = ChoiceItem('cancel', _('Cancel'))  # The payment is canceld by the user.
    Created = ChoiceItem('created', _('Created'))  # The order is created.
    Error = ChoiceItem('error', _('Error'))  # The payment gave an error.
    Pending = ChoiceItem('pending', _('Pending'))  # The payment is not completed or rejected.
    Refused = ChoiceItem('refused', _('Refused'))  # The payment could not be done.
