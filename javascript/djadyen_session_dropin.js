import { AdyenCheckout, Dropin, Card, Bancontact } from '@adyen/adyen-web';

import { PaymentComponents } from './supported_payments';

import { getSessionConfiguration } from './utils.js';

class SessionDropinPaymentCheckout {
    constructor() {
        this.config = document.querySelector('#djadyen-config');
    }

    createConfiguration() {
        if (this.config) return getSessionConfiguration(this.config.dataset);
        return null;
    }

    createDropinConfiguration() {
        try {
            const payment_types = JSON.parse(this.config.dataset.paymentTypes);

            const dropinConfiguration = {
                paymentMethodComponents: [],
                paymentMethodsConfiguration: {},
            };

            payment_types.forEach((payment) => {
                if (payment.payment_type in PaymentComponents) {
                    const [Component, getPaymentConfiguration, dropinName] =
                        PaymentComponents[payment.payment_type];

                    // Redirect components are handled by the session
                    if (dropinName === 'redirect') return;

                    dropinConfiguration.paymentMethodComponents.push(Component);
                    dropinConfiguration.paymentMethodsConfiguration[
                        dropinName
                    ] = getPaymentConfiguration(payment);
                } else {
                    console.error(
                        `Unknown payment type: ${payment.payment_type}`
                    );
                }
            });

            return dropinConfiguration;
        } catch (e) {
            console.error('Failed to parse payment types:', e);
        }

        return {};
    }

    async createCheckout() {
        const configuration = this.createConfiguration();
        if (!configuration) return console.error('Invalid configuration');

        const dropinConfiguration = this.createDropinConfiguration();

        const checkout = await AdyenCheckout(configuration);
        new Dropin(checkout, dropinConfiguration).mount(
            '#djadyen-dropin-container'
        );
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    const checkout = new SessionDropinPaymentCheckout();
    await checkout.createCheckout();
});
