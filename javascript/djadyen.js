import { AdyenCheckout } from "@adyen/adyen-web";

import { PaymentComponents } from "./supported_payments";

import "@adyen/adyen-web/styles/adyen.css";
import "./overwrites.css";

document.addEventListener("DOMContentLoaded", async () => {
    const config = document.querySelector("#djadyen-config");

    if (config) {
        const configuration = {
            environment: config.dataset.environment,
            clientKey: config.dataset.clientKey,
            locale: config.dataset.language,
            showPayButton: true,
            analytics: {
                enabled: false,
            },
            session: {
                id: config.dataset.sessionId,
                sessionData: config.dataset.sessionData,
            },
            onPaymentCompleted: (result) => {
                window.location = config.dataset.redirectUrl;
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

        const [Component, getPaymentConfiguration] =
            PaymentComponents[config.dataset.paymentType];
        const paymentConfiguration = GetPaymentConfiguration(config.dataset);

        const checkout = await AdyenCheckout(configuration);
        const component = new Component(checkout, paymentConfiguration).mount(
            "#djadyen-container"
        );
        if (paymentConfiguration.issuer) {
            setTimeout(() => {
                component.submit();
            }, 50);
        }
    }
});

document.addEventListener("DOMContentLoaded", async () => {
    const config = document.querySelector("#djadyen-status-config");

    if (config) {
        let newStatus = false;

        const poll = async ({ fn, validate, interval, maxAttempts }) => {
            let attempts = 0;

            const executePoll = async (resolve, reject) => {
                const result = await fn();
                attempts++;

                if (validate(result)) {
                    return resolve(result);
                } else if (maxAttempts && attempts === maxAttempts) {
                    return reject(new Error("Exceeded max attempts"));
                } else {
                    setTimeout(executePoll, interval, resolve, reject);
                }
            };

            return new Promise(executePoll);
        };

        const fetchNewStatus = async () => {
            const response = await fetch(config.dataset.statusUrl);
            const data = await response.json();
            return data;
        };

        poll({
            fn: fetchNewStatus,
            validate: (data) => {
                return !!data.updatedStatus;
            },
            interval: 10000,
        })
            .then((user) => {
                window.location.reload();
            })
            .catch((err) => console.error(err));
    }
});
