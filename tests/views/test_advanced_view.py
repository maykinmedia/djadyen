from django.urls import reverse
from django.utils.translation import get_language

import pytest

from tests.factories import PaymentOptionsFactory

pytestmark = [
    pytest.mark.django_db,
]

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
    assert response.template_name == ["adyen/advanced_pay.html"]


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


@pytest.mark.django_db
def test_advanced_view_ideal_bypass(
    client, setup_advanced_view, mock_redirect_ideal_payments_api
):
    """
    Test that the ideal payment option can bypass the web component
    and can redirect directly
    """

    url, order = setup_advanced_view

    ideal = PaymentOptionsFactory(adyen_name="ideal")

    order.payment_option = ideal
    order.save()

    response = client.get(url)

    assert response.status_code == 302
    assert response.url == "https://test.adyen.com/hpp/checkout.shtml"


@pytest.mark.django_db
def test_advanced_view_ideal_bypass_redirect(
    client, setup_advanced_view, mock_redirect_ideal_payments_api
):
    """
    Test that the ideal payment will not be redirected if there is a redirectResult
    """

    url, order = setup_advanced_view

    ideal = PaymentOptionsFactory(adyen_name="ideal")

    order.payment_option = ideal
    order.save()

    response = client.get(url, {"redirectResult": "ExampleRedirectCode"})

    assert response.status_code == 200
    assert response.template_name == ["adyen/advanced_pay.html"]
