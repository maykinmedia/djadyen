from django.contrib import admin

from .models import AdyenIssuer, AdyenNotification, AdyenPaymentOption


@admin.register(AdyenNotification)
class AdyenNotificationAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'is_processed', 'processed_at')
    list_filter = ('is_processed', 'created_at', 'processed_at')


@admin.register(AdyenPaymentOption)
class PaymentOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'adyen_name', 'is_active')
    list_filter = ('is_active', )


@admin.register(AdyenIssuer)
class IssuerAdmin(admin.ModelAdmin):
    list_display = ('name', 'payment_option')
    list_filter = ('payment_option', )
