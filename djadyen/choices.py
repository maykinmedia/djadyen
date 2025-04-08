from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class Status(TextChoices):
    Authorised = "authorised", _("Authorised")
    Cancel = "cancel", _("Cancel")
    Created = "created", _("Created")
    Error = "error", _("Error")
    Pending = "pending", _("Pending")
    Refused = "refused", _("Refused")
