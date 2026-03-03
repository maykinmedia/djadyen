from django.template import Context, Template
from django.urls import reverse

import pytest

from djadyen.choices import Status
from tests.factories import DonationFactory, OrderFactory

EXPECTED_PENDING_STATUS = [
    (Status.Authorised.value, False),
    (Status.Cancel.value, False),
    (Status.Created.value, True),
    (Status.Error.value, False),
    (Status.Pending.value, True),
    (Status.Refused.value, False),
]


# Polling
@pytest.mark.parametrize("status,shown", EXPECTED_PENDING_STATUS)
def test_adyen_status_polling_order_pending_status(status: Status, shown: bool) -> None:
    """
    Test that poling only happens for pending order statuses (Created, Pending)
    :param status: Ayden Status
    :param shown: if shown in the template
    """

    order = OrderFactory.build(status=status)
    status_url = reverse("order-status", args=[order.reference])

    out = Template(
        "{% load adyen_tags %}"
        "{% adyen_status_polling order=order status_url=status_url %}"
    ).render(Context({"order": order, "status_url": status_url}))
    assert (status_url in out) == shown


@pytest.mark.parametrize("status,shown", EXPECTED_PENDING_STATUS)
def test_adyen_status_polling_donation_pending_status(
    status: Status, shown: bool
) -> None:
    """
    Test that poling only happens for pending donation statuses (Created, Pending)
    :param status: Ayden Status
    :param shown: if shown in the template
    """

    donation = DonationFactory.build(status=status)
    status_url = reverse("donation-status", args=[donation.reference])

    out = Template(
        "{% load adyen_tags %}"
        "{% adyen_status_polling order=order status_url=status_url %}"
    ).render(Context({"order": donation, "status_url": status_url}))
    assert (status_url in out) == shown
