import AdyenCheckout from "@adyen/adyen-web";

import "@adyen/adyen-web/dist/adyen.css";
import "./overwrites.css";

document.addEventListener("DOMContentLoaded", async () => {
    const dropinConfig = document.querySelector("#djadyen-dropin-config");
    const config = document.querySelector("#djadyen-config");

    if (config) {
        const configuration = {
            environment: config.dataset.environment,
            clientKey: config.dataset.clientKey,
            session: {
                id: config.dataset.sessionId,
                sessionData: config.dataset.sessionData,
            },
            showPayButton: true,
            onPaymentCompleted: (result, component) => {
                console.info(result, component);
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

        const checkout = await AdyenCheckout(configuration);
        console.log(checkout.paymentMethodsResponse); // => { paymentMethods: [...], storedPaymentMethods: [...] }
        const component = checkout
            .create(config.dataset.paymentType)
            .mount("#djadyen-container");
    } else {
        console.error("No payment type found");
    }
});
