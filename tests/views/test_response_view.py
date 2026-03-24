import pytest

from djadyen.choices import Status

pytestmark = [
    pytest.mark.django_db,
]


def test_response_view_empty_get(django_app, setup_confirm_view):
    order, url = setup_confirm_view
    django_app.get(url, status=200)


def test_response_view_free_order(django_app, setup_confirm_view):
    order, url = setup_confirm_view
    order.amount = 0
    order.status = Status.Pending
    order.save()

    django_app.get(url, status=200)

    order.refresh_from_db()
    assert order.status == Status.Authorised


def test_response_view_redirect_success(
    django_app, setup_confirm_view, mock_successful_payment_details_api
):
    order, url = setup_confirm_view
    django_app.get(url, {"redirectResult": "SOME_DATA"}, status=200)

    order.refresh_from_db()
    assert order.status == Status.Authorised


def test_response_view_redirect_failure(
    django_app, setup_confirm_view, mock_refused_payment_details_api
):
    order, url = setup_confirm_view
    django_app.get(url, {"redirectResult": "SOME_DATA"}, status=200)

    order.refresh_from_db()
    assert order.status == Status.Error


@pytest.mark.skip("Broken settings")
def test_response_view_redirect_require_settings(
    django_app, setup_confirm_view, settings
):
    settings.DJADYEN_ENVIRONMENT = None

    order, url = setup_confirm_view
    with pytest.raises(NotImplementedError):
        django_app.get(url, {"redirectResult": "SOME_DATA"}, status=200)
