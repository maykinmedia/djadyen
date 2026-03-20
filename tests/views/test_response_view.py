from django.urls import reverse

import pytest

from tests.factories import OrderFactory

pytestmark = [
    pytest.mark.django_db,
]


def test_response_view_empty_get(django_app):
    order = OrderFactory()
    url = reverse("confirm", kwargs={"reference": order.reference})
    django_app.get(url, status=200)
