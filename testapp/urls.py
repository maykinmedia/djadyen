try:
    from django.urls import path, include
except Exception:
    from django.conf.urls import url as path, include

from django.contrib import admin

from .views import ConfirmationView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("confirm/", ConfirmationView.as_view(), name="confirm"),
    path(
        "adyen/notifications/",
        include("djadyen.notifications.urls", namespace="adyen-notifications"),
    ),
]
