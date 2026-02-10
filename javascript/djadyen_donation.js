import { AdyenCheckout, Donation } from '@adyen/adyen-web';

document.addEventListener('DOMContentLoaded', async () => {
    const config = document.querySelector('#djadyen-donation-config');

    if (config) {
        const configuration = {
            environment: config.dataset.environment,
            clientKey: config.dataset.clientKey,
            locale: config.dataset.language,
            countryCode: config.dataset.countryCode,
            analytics: {
                enabled: false,
            },
        };

        const handleOnDonate = (state, component) => {
            // state.isValid; // True or false. Specifies if the shopper has selected a donation amount.
            // state.data; // Provides the data that you need to pass in the `/donations` call.
            // component;// Provides the active Component instance that called this event.

            const form = document.djadyenDonationForm;
            form.amount.value = JSON.stringify(state.data.amount);
            form.submit();
        };

        const handleOnCancel = (state, component) => {
            // Show a message, unmount the Component, or redirect to another page.
            window.location.assign(config.dataset.cancelUrl);
        };

        let donationCampaign = { test: 'empty' };

        try {
            donationCampaign = JSON.parse(config.dataset.campaign);
        } catch (e) {
            console.warn('Invalid campaign to parsed:', e);
            return;
        }

        const donationConfig = {
            ...donationCampaign,
            showCancelButton: true,
            onDonate: handleOnDonate,
            onCancel: handleOnCancel,
        };

        const checkout = await AdyenCheckout(configuration);
        const donation = new Donation(checkout, donationConfig).mount(
            '#djadyen-donation-container'
        );
    }
});
