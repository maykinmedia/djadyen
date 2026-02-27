import re

from django.urls import reverse

import pytest

from tests.factories import OrderFactory


@pytest.fixture
def setup_advanced_view() -> tuple[str, OrderFactory]:
    order = OrderFactory()
    payments_api_url = reverse("advance_payment", args=[order.reference])
    return payments_api_url, order

