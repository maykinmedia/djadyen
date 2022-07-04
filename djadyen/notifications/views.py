import json
import logging

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from ..models import AdyenNotification

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
        logger.debug(_("New notification(s)"))
        json_params = json.loads(request.body)
        notification_items = json_params.get("notificationItems", [])
        for notification_item in notification_items:
            notification = AdyenNotification.objects.create(
                notification=json.dumps(notification_item.get("NotificationRequestItem"))
            )
            logger.debug(_("Notification saved | id: %s"), notification.id)

        return HttpResponse("[accepted]")
