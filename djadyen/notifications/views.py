import json
import logging

from django.http import HttpResponse, HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from ..models import AdyenNotification
from .hmac import create_hmac

logger = logging.getLogger(__name__)


class NotificationView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(NotificationView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Note that Adyen requires SSL/TLS client-certificate validation
        but we don't do that. We do validate that the notification originates
        from Adyen by verifying the HMAC.

        TODO: Validate SSL/TLS client-certificate validation.
        """
        logger.debug(_('New notification'))

        # After we verify that the notification originates from Adyen,
        # we store it in our database.

        hmac_value = create_hmac(request.POST)

        if ('additionalData.hmacSignature' not in request.POST or
                hmac_value != request.POST['additionalData.hmacSignature']):
            return HttpResponseForbidden()

        # TODO Validate request.POST. External data should really be always
        # be validated.

        json_params = json.dumps(request.POST)

        notification = AdyenNotification.objects.create(notification=json_params)
        logger.debug(_('Notification saved | id: %s'), notification.id)

        return HttpResponse('[accepted]')
