from datetime import timedelta

from django.apps import apps
from django.core.management.base import BaseCommand
from django.utils import timezone

from djadyen import settings
from djadyen.choices import Status
from djadyen.models import AdyenNotification


class Command(BaseCommand):
    help = "Process the adyen notifications that are not processed yet."

    def handle(self, *args, **options):
        order_models = [apps.get_model(model) for model in settings.ADYEN_ORDER_MODELS]

        #
        # N.B. In our implementations there use to be a limit at how far back in the past we
        # would go to process notifications. I'm not sure why it existed, so i've removed it.
        #

        # Process notifications which have been sent by Adyen.
        for notification in AdyenNotification.objects.filter(is_processed=False):
            notification_data = notification.get_notification_data()
            reference = notification_data.get('merchantReference')

            for order_model in order_models:
                orders = order_model.objects.filter(reference=reference)

                for order in orders:
                    order.process_notification(notification)

        # After five days of an Order having status 'Pending', move them to 'Error'
        five_days_ago = timezone.now() - timedelta(days=5)
        for order_model in order_models:
            for obj in order_model.objects.filter(
                status=Status.Pending,
                created_on__lte=five_days_ago
            ):
                obj.status = Status.Error
                obj.save()
