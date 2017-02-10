from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^app/', include('tests.app.urls')),
    url(r'^adyen/notifications/', include('djadyen.notifications.urls', namespace='adyen-notifications')),
]
