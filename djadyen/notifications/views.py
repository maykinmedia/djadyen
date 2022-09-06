import json
import logging

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from ..models import AdyenNotification
from .signing import get_signature

logger = logging.getLogger("adyen")


class NotificationView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(NotificationView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """ """
        logger.debug(_("New notification(s)"))
        json_params = json.loads(request.body)
        notification_items = json_params.get("notificationItems", [])
        successfully_created = True
        for notification_item in notification_items:
            nir = notification_item.get("NotificationRequestItem")
            signature = nir.get("additionalData", {}).get("hmacSignature")
            create_notification = False
            if signature:
                compare_signature = get_signature(nir)
                if signature == compare_signature:
                    create_notification = True

            if create_notification:
                notification = AdyenNotification.objects.create(
                    notification=json.dumps(nir)
                )
                logger.debug(_("Notification saved | id: %s"), notification.id)
            else:
                successfully_created = False

        if successfully_created:
            return HttpResponse("[accepted]")
        return HttpResponse("[rejected]")
