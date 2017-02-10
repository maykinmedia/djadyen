import json
import logging

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from ..models import AdyenNotification

logger = logging.getLogger(__name__)


class NotificationView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(NotificationView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logger.debug(_('New notification'))
        logger.debug(request.POST)
        json_params = json.dumps(request.POST)
        if request.POST:
            notification = AdyenNotification.objects.create(notification=json_params)
            logger.debug(_('Notification saved | id: %s'), notification.id)
        return HttpResponse('[accepted]')
