from django.contrib import admin
from django.urls import include, path

from .views import ConfirmationView, PaymentView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("<uuid:reference>/payment/", PaymentView.as_view(), name="payment"),
    path("<uuid:reference>/confirm/", ConfirmationView.as_view(), name="confirm"),
    path(
        "adyen/notifications/",
        include("djadyen.notifications.urls", namespace="adyen-notifications"),
    ),
]
