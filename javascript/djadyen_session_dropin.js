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

            let dropin_configuration = {
                paymentMethodComponents: [],
                paymentMethodsConfiguration: {},
            };

            payment_types.forEach((payment) => {
                const [Component, getPaymentConfiguration, dropin_name] =
                    PaymentComponents[payment.payment_type];

                // Redirect components are handled by the session
                if (dropin_name === 'redirect') return;

                dropin_configuration.paymentMethodComponents.push(Component);
                dropin_configuration.paymentMethodsConfiguration[dropin_name] =
                    getPaymentConfiguration(payment);
            });

            return dropin_configuration;
        } catch (e) {
            console.error('Failed to parse payment types:', e);
        }

        return {};
    }

    async createCheckout() {
        const configuration = this.createConfiguration();
        if (!configuration) return console.error('Invalid configuration');

        console.log(configuration);

        const dropinConfiguration = this.createDropinConfiguration();

        console.log(dropinConfiguration);

        const checkout = await AdyenCheckout(configuration);
        const dropin = new Dropin(checkout, dropinConfiguration).mount(
            '#djadyen-dropin-container'
        );
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    const checkout = new SessionDropinPaymentCheckout();
    await checkout.createCheckout();
});
