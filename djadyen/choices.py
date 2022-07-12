from django.utils.translation import gettext_lazy as _

from djchoices import ChoiceItem, DjangoChoices


class Status(DjangoChoices):
    Authorised = ChoiceItem("authorised", _("Authorised"))
    Cancel = ChoiceItem("cancel", _("Cancel"))
    Created = ChoiceItem("created", _("Created"))
    Error = ChoiceItem("error", _("Error"))
    Pending = ChoiceItem("pending", _("Pending"))
    Refused = ChoiceItem("refused", _("Refused"))
