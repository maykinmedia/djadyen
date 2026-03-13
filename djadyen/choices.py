from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class Status(TextChoices):
    Authorised = "Authorised", _("Authorised")
    Cancel = "Cancel", _("Cancel")
    Created = "Created", _("Created")
    Error = "Error", _("Error")
    Pending = "Pending", _("Pending")
    Refused = "Refused", _("Refused")


class AdyenComponentSupport(TextChoices):
    """
    Adyen-web component support options
    """

    Supported = "supported", _("Supported")
    Unsupported = "unsupported", _("Unsupported")
    Unknown = "unknown", _("Unknown")
