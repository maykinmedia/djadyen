from django.urls import path

from .views import NotificationView

app_name = 'adyen-notifications'
urlpatterns = [
    path('/', NotificationView.as_view(), name="notification"),
]
