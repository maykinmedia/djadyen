# 2.0.0

-   Switched to Web Drop-in and Web Compoments instead of HPP pages

# 1.1.1

-   Fixed the processing of created orders by notifications.
-   Fixed that notifications older than `ADYEN_HANDLE_NOTIFICATION_MINUTES_AGO` minutes will be processed.

# 1.1.0

-   Removed the auto-fetch option.
-   Improved README documentation.
-   Refectored some core code to make it more reusable.
-   Validate the notification that is send.
-   Added a default management command to handle the notifications.

# 1.0.1

-   Fixed the bug where not all fields that were passed were created and send to adyen. Causing an error.

# 1.0.0

-   Created an initial release that supports Django 1.11, Django 2.0 and python 3.4+.
