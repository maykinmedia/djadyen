from django.contrib import admin
from django.urls import include, path

from .views import (
    AdvancedPaymentView,
    ConfirmationView,
    DonationView,
    PaymentDetailsAPIView,
    PaymentsAPIView,
    PaymentView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("<uuid:reference>/payment/", PaymentView.as_view(), name="payment"),
    path("<uuid:reference>/confirm/", ConfirmationView.as_view(), name="confirm"),
    path(
        "adyen/notifications/",
        include("djadyen.notifications.urls", namespace="adyen-notifications"),
    ),
    # Advanced checkout paths
    path(
        "<uuid:reference>/advanced_payment/",
        AdvancedPaymentView.as_view(),
        name="advance_payment",
    ),
    path(
        "api/<uuid:reference>/payments/", PaymentsAPIView.as_view(), name="payments_api"
    ),
    path(
        "api/<uuid:reference>/payment_details/",
        PaymentDetailsAPIView.as_view(),
        name="payment_details_api",
    ),
    path("<uuid:reference>/donation/", DonationView.as_view(), name="donation"),
]
