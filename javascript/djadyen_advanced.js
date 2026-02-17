import { AdyenCheckout } from '@adyen/adyen-web';

import { PaymentComponents } from './supported_payments';

class AdvancedPaymentCheckout {
    constructor() {
        this.config = document.querySelector('#djadyen-config');
    }

    async makePaymentsCall(data) {
        const response = await fetch(this.config.dataset.paymentsEndpoint, {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': this.config.dataset.csrfToken,
            },
            credentials: 'same-origin',
            body: JSON.stringify(data),
        });
        return await response.json();
    }

    async makeDetailsCall(data) {
        return await fetch(this.config.dataset.paymentDetailsEndpoint, {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': this.config.dataset.csrfToken,
            },
            credentials: 'same-origin',
            body: JSON.stringify(data),
        }).then((response) => response.json());
    }

    async handleRedirectResult() {
        // 1. Get the redirectResult from your return URL.
        const urlParams = new URLSearchParams(window.location.search);
        const redirectResult = urlParams.get('redirectResult');

        if (redirectResult) {
            // 2. Pass the redirectResult to your server.
            // 3. Your server makes the /payments/details request. Adyen's server processes the encoded redirectResult value.
            try {
                const data = await this.makeDetailsCall({ redirectResult });
                // Verify the resultCode from your server's response.
                if (data && data.resultCode === 'Authorised') {
                    console.log('Payment authorized successfully!');
                    // Handle successful payment authorization. For example: show a confirmation message or redirect the shopper to a confirmation page.
                    window.location.assign(this.config.dataset.redirectUrl);
                } else {
                    console.log('Payment failed or denied.');
                    // Handle payment failure. For example: show an error message or redirect the shopper to an error page.
                    window.location.assign(this.config.dataset.redirectUrl);
                }
            } catch (error) {
                // Handle network errors or issues with server communication.
                console.error(
                    'Error sending redirect result or processing server response:',
                    error
                );
            }
        }
    }

    createConfiguration() {
        if (this.config) {
            return {
                clientKey: this.config.dataset.clientKey,
                environment: this.config.dataset.environment,
                amount: {
                    value: this.config.dataset.amount,
                    currency: this.config.dataset.currency,
                },
                locale: this.config.dataset.language,
                countryCode: this.config.dataset.countryCode,
                // The full /paymentMethods response object from your server. Contains the payment methods configured in your account.
                // paymentMethodsResponse: paymentMethodsResponse,
                onSubmit: async (state, component, actions) => {
                    try {
                        // Make a POST /payments request from your server.
                        const result = await this.makePaymentsCall(state.data);

                        // If the /payments request from your server fails, or if an unexpected error occurs.
                        if (!result.resultCode) return actions.reject();

                        const { resultCode, action, order, donationToken } =
                            result;
                        console.log(resultCode, action);

                        // If the /payments request request from your server is successful, you must call this to resolve whichever of the listed objects are available.
                        // You must call this, even if the result of the payment is unsuccessful.
                        actions.resolve({
                            resultCode,
                            action,
                            order,
                            donationToken,
                        });
                    } catch (error) {
                        console.error('onSubmit', error);
                        actions.reject();
                    }
                },
                onAdditionalDetails: async (state, component, actions) => {
                    try {
                        // Make a POST /payments/details request from your server.
                        const result = await this.makeDetailsCall(state.data);

                        // If the /payments/details request from your server fails, or if an unexpected error occurs.
                        if (!result.resultCode) return actions.reject();

                        const { resultCode, action, order, donationToken } =
                            result;

                        // If the /payments/details request from your server is successful, you must call this to resolve whichever of the listed objects are available.
                        // You must call this, even if the result of the payment is unsuccessful.
                        actions.resolve({
                            resultCode,
                            action,
                            order,
                            donationToken,
                        });
                    } catch (error) {
                        console.error('onSubmit', error);
                        actions.reject();
                    }
                },
                onPaymentCompleted: (result, component) => {
                    console.info('Completed', result, component);
                    window.location.assign(this.config.dataset.redirectUrl);
                },
                onPaymentFailed: (result, component) => {
                    console.info('Failed', result, component);
                    window.location.assign(this.config.dataset.redirectUrl);
                },
                onError: (error, component) => {
                    console.error(
                        error.name,
                        error.message,
                        error.stack,
                        component
                    );
                },
            };
        }
        return null;
    }

    async createCheckout() {
        // Call this function when your page loads.
        await this.handleRedirectResult();

        const configuration = this.createConfiguration();
        if (configuration) {
            const checkout = await AdyenCheckout(configuration);
            const [Component, getPaymentConfiguration] =
                PaymentComponents[this.config.dataset.paymentType];
            const paymentConfiguration = getPaymentConfiguration(
                this.config.dataset
            );
            new Component(checkout, paymentConfiguration).mount(
                '#djadyen-advanced-container'
            );
        } else {
            console.error('Invalid configuration');
        }
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    let checkout = new AdvancedPaymentCheckout();
    await checkout.createCheckout();
});
