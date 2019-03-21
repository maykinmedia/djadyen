from django.conf.urls import url

from .views import (
    Confirmation2View, ConfirmationView, My2AdyenRequestView,
    My3AdyenRequestView, MyAdyenRequestView
)

urlpatterns = [
    url(r'^confirm/$', ConfirmationView.as_view(), name="confirm"),
    url(r'^confirm2/$', Confirmation2View.as_view(), name="confirm2"),
    url(r'^(?P<reference>[\w-]+)/$', MyAdyenRequestView.as_view(), name="redirect"),
    url(r'^2/(?P<reference>[\w-]+)/$', My2AdyenRequestView.as_view(), name="redirect2"),
    url(r'^3/(?P<reference>[\w-]+)/$', My3AdyenRequestView.as_view(), name="redirect3"),
]
