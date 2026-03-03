from django.urls import reverse
from django.utils.translation import get_language

import pytest


@pytest.mark.django_db()
def test_advanced_view_no_order(client):
    """
    Test that the advanced view requires an order or 404s
    """
    advanced_url = reverse(
        "advance_payment", args=["00000000-0000-0000-0000-000000000000"]
    )

    response = client.get(advanced_url)
    assert response.status_code == 404


@pytest.mark.django_db()
def test_advanced_view_simple(client, setup_advanced_view):
    """
    Test that the view renders correctly with a simple order
    """
    url, order = setup_advanced_view
    response = client.get(url)

    order.refresh_from_db()
    assert response.status_code == 200


@pytest.mark.django_db()
def test_advanced_view_free_price(client, setup_advanced_view):
    """
    Test that the user is redirected to the payment page if the order is free
    """
    url, order = setup_advanced_view
    order.amount = 0
    order.save()

    response = client.get(url)

    order.refresh_from_db()
    assert response.status_code == 302


@pytest.mark.django_db()
def test_advanced_view_language_code(client, setup_advanced_view):
    """
    Test that the adyen locale is used if get_locale is overridden
    """
    url, order = setup_advanced_view

    response = client.get(url)

    assert get_language() == "en"
    assert response.context["adyen_language"] == "en-US"
