function getCommonPaymentConfiguration(dataset) {
    const commonPaymentConfiguration = {};

    // Add custom styles from Django settings if provided
    if (dataset.styles) {
        try {
            paymentConfiguration.styles = JSON.parse(dataset.styles);
        } catch (e) {
            console.error("Failed to parse DJADYEN_STYLES:", e);
        }
    }

    return commonPaymentConfiguration;
}

/**
 * Creates payment configuration for componnent that use issuers
 * @param {*} dataset
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
 * Creates payment configuration for componnent that use issuers
 * @param {*} dataset object
 * @returns paymentConfiguration
 */
export function getBrandConfiguration(dataset) {
    const paymentConfiguration = getCommonPaymentConfiguration(dataset);
    if (dataset.issuers) {
        let issuers = JSON.parse(dataset.issuers);
        paymentConfiguration.brands = issuers.map(({ adyen_id }) => adyen_id);
    }

    return paymentConfiguration;
}
