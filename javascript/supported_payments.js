import {
    Bancontact,
    BankTransfer,
    Card,
    Redirect,
    SepaDirectDebit,
} from '@adyen/adyen-web';

import { getBrandConfiguration, getRedirectConfiguration } from './utils';

export const PaymentComponents = {
    alipay: [Redirect, getRedirectConfiguration, 'redirect'],
    bankTransfer_IBAN: [BankTransfer, getRedirectConfiguration, 'banktransfer'],
    bcmc: [Bancontact, getBrandConfiguration, 'bancontact'],
    ebanking_FI: [Redirect, getRedirectConfiguration, 'redirect'],
    ideal: [Redirect, getRedirectConfiguration, 'redirect'],
    sepadirectdebit: [SepaDirectDebit, () => ({}), 'sepadirectdebit'],
    scheme: [Card, getBrandConfiguration, 'card'],
    directEbanking: [Redirect, getRedirectConfiguration, 'redirect'],
};
