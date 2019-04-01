from django.conf.urls import url

from .views import NotificationView

app_name = 'adyen-notifications'
urlpatterns = [
    url(r'^$', NotificationView.as_view(), name="notification"),
]
