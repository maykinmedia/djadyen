import { Card, Redirect } from "@adyen/adyen-web";

import { getBrandConfiguration } from "./utils";

export const PaymentComponents = {
    scheme: [Card, getBrandConfiguration],
    ideal: [
        Redirect,
        () => ({
            type: "ideal",
        }),
    ],
};
