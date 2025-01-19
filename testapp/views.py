from djadyen.choices import Status
from djadyen.views import AdyenResponseView

from .models import Order


class ConfirmationView(AdyenResponseView):
    template_name = "app/confirmation.html"
    model = Order

    def handle_authorised(self):
        self.order.status = Status.Authorised
        return self.done()

    def handle_pending(self):
        self.order.status = Status.Pending
        return self.done()

    def handle_refused(self):
        self.order.status = Status.Refused
        return self.done()

    def handle_error(self):
        self.order.status = Status.Error
        return self.done()

    def handle_canceled(self):
        self.order.status = Status.Cancel
        return self.done()

    def handle_default(self):
        pass
