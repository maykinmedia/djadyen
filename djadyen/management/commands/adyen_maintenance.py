from datetime import timedelta

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from djadyen import settings
from djadyen.choices import Status
from djadyen.models import AdyenNotification


class Command(BaseCommand):
    help = "Process the adyen notifications that are not processed yet."

    def handle(self, *args, **options):
        # Add a timeout to not process all the notifications after the view is already processed.
        time_ago = timezone.now() - timedelta(minutes=settings.ADYEN_HANDLE_NOTIFICATION_MINUTES_AGO)

        order_models = [apps.get_model(model) for model in settings.ADYEN_ORDER_MODELS]

        # Process notifications which have been sent by Adyen.
        for notification in AdyenNotification.objects.filter(is_processed=False, created_at__lte=time_ago):
            notification_data = notification.get_notification_data()
            reference = notification_data.get('merchantReference')

            for order_model in order_models:
                #
                # TOOD: Ugh, okay so we process only 'Pending' orders, this might
                # or might not be correct, I don't understand the adyen state machine
                # well enough.
                #
                # The reason this is done to avoid that an order, which is already processed
                # in the return URL, to be processed again by a notification.
                #
                orders = order_model.objects.filter(reference=reference).filter(
                    Q(status=Status.Pending) | Q(status=Status.Created)
                )

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
