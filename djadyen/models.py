import json
import logging
from uuid import uuid4

from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from djadyen import settings

from .choices import Status

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class AdyenNotification(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    notification = models.TextField()
    is_processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.created_at.strftime('%c')

    def get_notification_data(self):
        return json.loads(self.notification)

    def has_status(self, status):
        data = self.get_notification_data()
        event_code = data.get('eventCode')
        merchant_account_code = data.get('merchantAccountCode')
        return (
            event_code == status and
            merchant_account_code == settings.ADYEN_MERCHANT_ACCOUNT
        )

    def is_authorised(self, require_success=True):
        data = self.get_notification_data()
        success = data.get('success') == 'true'
        has_status = self.has_status('AUTHORISATION')

        if not require_success:
            return has_status

        return has_status and success

    def is_error(self):
        return self.has_status('ERROR')

    def is_cancelled(self):
        return self.has_status('CANCEL')

    def is_refused(self):
        return self.has_status('REFUSED')

    def mark_processed(self, commit=True):
        self.is_processed = True
        self.processed_at = timezone.now()
        if commit:
            self.save()


@python_2_unicode_compatible
class AdyenPaymentOption(models.Model):
    name = models.CharField(max_length=200, default="")
    adyen_name = models.CharField(max_length=200, default="")
    guid = models.CharField(max_length=36, verbose_name=_('GUID'), default="")
    image = models.ImageField(null=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class AdyenIssuer(models.Model):
    payment_option = models.ForeignKey(AdyenPaymentOption, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, default="")
    adyen_id = models.CharField(max_length=200, default="")

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class AdyenOrder(models.Model):
    status = models.CharField(max_length=200, choices=Status.choices, default=Status.Created)
    created_on = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=200, default="", blank=True)
    psp_reference = models.CharField(max_length=200, default="", blank=True)
    email = models.EmailField()

    payment_option = models.ForeignKey(AdyenPaymentOption, blank=True, null=True, on_delete=models.SET_NULL)
    issuer = models.ForeignKey(AdyenIssuer, null=True, blank=True, on_delete=models.SET_NULL)

    __old_status = None

    class Meta:
        abstract = True

    def __str__(self):
        return '{}'.format(self.reference)

    def __init__(self, *args, **kwargs):
        super(AdyenOrder, self).__init__(*args, **kwargs)
        self.__old_status = self.status

    def process_notification(self, notification):
        if notification.is_authorised():
            self.status = Status.Authorised
            self.save()

            notification.mark_processed()
        elif notification.is_error():
            self.status = Status.Error
            self.save()

            notification.mark_processed()
        elif notification.is_cancelled():
            self.status = Status.Cancel
            self.save()

            notification.mark_processed()
        elif notification.is_refused():
            self.status = Status.Refused
            self.save()

            notification.mark_processed()

        logger.error("Can't process notification with pk %d", notification.pk)

        # Ignore anything else for now.

    def get_price_in_cents(self):
        """
        :return int Return the price in cents for this order.
        """
        raise NotImplementedError

    def save(self, can_change=False, *args, **kwargs):
        if not self.reference:
            self.reference = uuid4()

        if settings.ADYEN_REFETCH_OLD_STATUS and self.id:
            self.__old_status = self._meta.model.objects.get(pk=self.id).status

        if self.status != self.__old_status:
            if self.__old_status == Status.Authorised:
                logger.warning(
                    _("Order ref: %s | Tried to change the status from 'Authorised' to '%s'. "),
                    self.reference, self.status)
                self.status = self.__old_status
            else:
                logger.warning(
                    _("Order ref: %s | Changed the status from '%s' to '%s'"),
                    self.reference, self.__old_status, self.status)
                self.__old_status = self.status

        return super(AdyenOrder, self).save(*args, **kwargs)
