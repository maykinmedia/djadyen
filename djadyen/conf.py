"""
Configuration module for djadyen settings.
"""

from django.conf import settings


def get_adyen_styles():
    """
    Get custom Adyen styles from Django settings.

    Returns the DJADYEN_STYLES setting or an empty dict if not configured.
    These styles are passed to the Adyen payment component configuration.

    Example setting:
        DJADYEN_STYLES = {
            'base': {
                'color': '#000000',
                'fontSize': '16px',
                'fontFamily': 'Arial, sans-serif',
            },
            'placeholder': {
                'color': '#999999',
            },
            'error': {
                'color': '#ff0000',
            }
        }

    Returns:
        dict: Custom Adyen component styles configuration
    """
    return getattr(settings, "DJADYEN_STYLES", {})
