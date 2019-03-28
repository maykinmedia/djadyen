try:
    from django.urls import path, include
except:
    from django.conf.urls import url as path, include

from django.contrib import admin

urlpatterns = [
    path(r'^admin/', admin.site.urls),
    path(r'^app/', include('tests.app.urls')),
    path(r'^adyen/notifications/', include('djadyen.notifications.urls', namespace='adyen-notifications')),
]
