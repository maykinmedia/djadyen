import AdyenCheckout from "@adyen/adyen-web";

import "@adyen/adyen-web/dist/adyen.css";
import "./overwrites.css";

document.addEventListener("DOMContentLoaded", async () => {
    const config = document.querySelector("#djadyen-config");

    if (config) {
        const configuration = {
            environment: config.dataset.environment,
            clientKey: config.dataset.clientKey,
            analytics: {
                enabled: false,
            },
            session: {
                id: config.dataset.sessionId,
                sessionData: config.dataset.sessionData,
            },
            showPayButton: true,
            onPaymentCompleted: (result) => {
                window.location = `${config.dataset.redirectUrl}?sessionId=${result.sessionData}`;
            },
            onError: (error, component) => {
                console.exception(
                    error.name,
                    error.message,
                    error.stack,
                    component
                );
            },
        };

        const paymentConfiguration = {};
        if (config.dataset.issuer) {
            paymentConfiguration.issuer = config.dataset.issuer;
        }

        const checkout = await AdyenCheckout(configuration);
        const component = checkout
            .create(config.dataset.paymentType, paymentConfiguration)
            .mount("#djadyen-container");
    } else {
        console.error("No payment type found");
    }
});
