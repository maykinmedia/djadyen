from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from djadyen.choices import AdyenComponentSupport
from djadyen.models import AdyenIssuer, AdyenNotification, AdyenPaymentOption


@admin.register(AdyenNotification)
class AdyenNotificationAdmin(admin.ModelAdmin):
    list_display = ("created_at", "is_processed", "processed_at")
    list_filter = ("is_processed", "created_at", "processed_at")


class AdyenIssuerInline(admin.TabularInline):
    model = AdyenIssuer
    extra = 1


@admin.register(AdyenPaymentOption)
class PaymentOptionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "adyen_name",
        "is_active",
        "show_issuers",
        "component_support",
    )
    list_filter = ("is_active",)
    inlines = [AdyenIssuerInline]
    search_fields = ("name", "adyen_name")

    @admin.display(description=_("Issuers/Brands"), empty_value="---")
    def show_issuers(self, obj):
        issuers = obj.adyenissuer_set.all()
        if issuers:
            return ", ".join([issuer.adyen_id for issuer in issuers])
        return None

    @admin.display(description=_("Supports Adyen Web"), boolean=True)
    def component_support(self, obj):
        if obj.get_adyen_component_support() == AdyenComponentSupport.Unknown:
            return None
        return obj.get_adyen_component_support() == AdyenComponentSupport.Supported


@admin.register(AdyenIssuer)
class IssuerAdmin(admin.ModelAdmin):
    list_display = ("name", "payment_option")
    list_filter = ("payment_option",)
