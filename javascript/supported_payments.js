import {
    Bancontact,
    BankTransfer,
    Card,
    Redirect,
    SepaDirectDebit,
} from '@adyen/adyen-web';

import { getBrandConfiguration, getRedirectConfiguration } from './utils';

export const PaymentComponents = {
    alipay: [Redirect, getRedirectConfiguration],
    bankTransfer_IBAN: [BankTransfer, getRedirectConfiguration],
    bcmc: [Bancontact, getBrandConfiguration],
    ebanking_FI: [Redirect, getRedirectConfiguration],
    ideal: [Redirect, getRedirectConfiguration],
    sepadirectdebit: [SepaDirectDebit, () => ({})],
    scheme: [Card, getBrandConfiguration],
};
