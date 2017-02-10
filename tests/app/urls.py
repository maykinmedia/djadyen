from django.conf.urls import url

from .views import ConfirmationView, Confirmation2View, Confirmation3View, MyAdyenRequestView, My2AdyenRequestView


urlpatterns = [
    url(r'^confirm/$', ConfirmationView.as_view(), name="confirm"),
    url(r'^confirm2/$', Confirmation2View.as_view(), name="confirm2"),
    url(r'^confirm3/$', Confirmation3View.as_view(), name="confirm3"),
    url(r'^(?P<reference>[\w-]+)/$', MyAdyenRequestView.as_view(), name="redirect"),
    url(r'^2/(?P<reference>[\w-]+)/$', My2AdyenRequestView.as_view(), name="redirect2"),
]
