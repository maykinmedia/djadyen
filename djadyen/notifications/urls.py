try:
    from django.urls import path
except Exception:
    from django.conf.urls import url as path

from .views import NotificationView

app_name = "adyen-notifications"
urlpatterns = [
    path("", NotificationView.as_view(), name="notification"),
]
