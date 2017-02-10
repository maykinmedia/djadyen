import logging
from uuid import uuid4

from django.db import models
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
    payment_option = models.ForeignKey(AdyenPaymentOption)
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

    payment_option = models.ForeignKey(AdyenPaymentOption, blank=True, null=True)
    issuer = models.ForeignKey(AdyenIssuer, null=True, blank=True)

    __old_status = None

    class Meta:
        abstract = True

    def __str__(self):
        return '{}'.format(self.reference)

    def __init__(self, *args, **kwargs):
        super(AdyenOrder, self).__init__(*args, **kwargs)
        self.__old_status = self.status

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
