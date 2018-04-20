try:
    from django.urls import path
except:
    from django.conf.urls import url as path

from .views import NotificationView

app_name = 'adyen-notifications'
urlpatterns = [
    path(r'^$', NotificationView.as_view(), name="notification"),
]
