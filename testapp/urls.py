try:
    from django.urls import include, path
except Exception:
    from django.conf.urls import url as path, include

from django.contrib import admin

from djadyen.views import AdyenPaymentView

from .views import ConfirmationView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("<uuid:reference>/payment/", AdyenPaymentView.as_view(), name="payment"),
    path("<uuid:reference>/confirm/", ConfirmationView.as_view(), name="confirm"),
    path(
        "adyen/notifications/",
        include("djadyen.notifications.urls", namespace="adyen-notifications"),
    ),
]
