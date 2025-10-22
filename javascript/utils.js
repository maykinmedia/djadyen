/**
 * Creates payment configuration for common components
 * @param {DOMStringMap} dataset object
 * @returns paymentConfiguration
 */
function getCommonPaymentConfiguration(dataset) {
    const commonPaymentConfiguration = {};

    // Add custom styles from Django settings if provided
    if (dataset.styles) {
        try {
            commonPaymentConfiguration.styles = JSON.parse(dataset.styles);
        } catch (e) {
            console.error("Failed to parse DJADYEN_STYLES:", e);
        }
    }

    return commonPaymentConfiguration;
}

/**
 * Creates payment configuration for components that use issuers
 * @param {DOMStringMap} dataset
 * @returns paymentConfiguration
 */
export function getIssuerConfiguration(dataset) {
    const paymentConfiguration = getCommonPaymentConfiguration(dataset);

    if (dataset.issuer) {
        paymentConfiguration.issuer = dataset.issuer;
    }

    return paymentConfiguration;
}

/**
 * Creates payment configuration for components that use issuers
 * @param {DOMStringMap} dataset object
 * @returns paymentConfiguration
 */
export function getBrandConfiguration(dataset) {
    const paymentConfiguration = getCommonPaymentConfiguration(dataset);
    if (dataset.issuers) {
        try {
            const issuers = JSON.parse(dataset.issuers);
            paymentConfiguration.brands = issuers.map(
                ({ adyen_id }) => adyen_id
            );
        } catch (e) {
            console.error("Failed to parse issuers:", e);
        }
    }

    return paymentConfiguration;
}

/**
 * Returns Redirect configuraiton
 * @param {*} dataset
 * @returns
 */
export function getRedirectConfiguration(dataset) {
    return { type: dataset.paymentType };
}
