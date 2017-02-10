from django.conf.urls import url

from .views import NotificationView


urlpatterns = [
    url(r'^$', NotificationView.as_view(), name="notification"),
]
