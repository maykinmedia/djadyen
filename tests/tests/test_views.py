from django.core.urlresolvers import reverse

from django_webtest import WebTest
from webtest import AppError

from djadyen import settings
from djadyen.views import AdyenSigMixin

from .factories import IssuerFactory, OrderFactory, PaymentOptionsFactory


class MyRedirectViewTests(WebTest):
    def setUp(self):
        self.order = OrderFactory()
        self.url = reverse('redirect', kwargs={'reference': self.order.reference})

    def test_redirection_page(self):
        response = self.app.get(self.url)
        self.assertEqual(response.status_code, 200)

        form = response.forms['redirect-form']
        response = form.submit()
        self.assertEqual(response.status_code, 302)

    def test_redirection_page_with_brand_code(self):
        self.order.payment_option = PaymentOptionsFactory()
        self.order.save()
        response = self.app.get(self.url)
        self.assertEqual(response.status_code, 200)

        form = response.forms['redirect-form']
        response = form.submit()
        self.assertEqual(response.status_code, 302)

    def test_redirection_page_with_issuer(self):
        payment_option = PaymentOptionsFactory()
        self.order.payment_option = payment_option
        self.order.issuer = IssuerFactory(payment_option=payment_option)
        self.order.save()
        response = self.app.get(self.url)
        self.assertEqual(response.status_code, 200)

        form = response.forms['redirect-form']
        response = form.submit()
        self.assertEqual(response.status_code, 302)

    def test_redirection_page_adyen_enabled(self):
        settings.ADYEN_ENABLED = True
        response = self.app.get(self.url)
        self.assertEqual(response.status_code, 200)

        form = response.forms['redirect-form']
        with self.assertRaises(AppError):
            response = form.submit()
        settings.ADYEN_ENABLED = False

    def test_redirection_page_with_brand_code_adyen_enabled(self):
        settings.ADYEN_ENABLED = True
        self.order.payment_option = PaymentOptionsFactory()
        self.order.save()
        response = self.app.get(self.url)
        self.assertEqual(response.status_code, 200)

        form = response.forms['redirect-form']
        with self.assertRaises(AppError):
            response = form.submit()
        settings.ADYEN_ENABLED = False

    def test_redirection_page_with_issuer_adyen_enabled(self):
        settings.ADYEN_ENABLED = True
        payment_option = PaymentOptionsFactory()
        self.order.payment_option = payment_option
        self.order.issuer = IssuerFactory(payment_option=payment_option)
        self.order.save()
        response = self.app.get(self.url)
        self.assertEqual(response.status_code, 200)

        form = response.forms['redirect-form']
        with self.assertRaises(AppError):
            response = form.submit()
        settings.ADYEN_ENABLED = False

    def test_redirection_page_post_with_adyen_enabled(self):
        response = self.app.get(self.url)
        self.assertEqual(response.status_code, 200)

        form = response.forms['redirect-form']
        settings.ADYEN_ENABLED = True
        with self.assertRaises(AppError):
            response = form.submit()
        settings.ADYEN_ENABLED = False


class My2RedirectViewTests(WebTest):
    def setUp(self):
        self.order = OrderFactory(email='')
        self.url = reverse('redirect2', kwargs={'reference': self.order.reference})

    def test_redirection_page(self):
        response = self.app.get(self.url)
        self.assertEqual(response.status_code, 200)

        form = response.forms['redirect-form']
        response = form.submit()
        self.assertEqual(response.status_code, 302)

    def test_redirection_page_no_email(self):
        response = self.app.get(self.url)
        self.assertEqual(response.status_code, 200)

        form = response.forms['redirect-form']
        response = form.submit()
        self.assertEqual(response.status_code, 302)


class My3RedirectViewTests(WebTest):
    def setUp(self):
        self.order = OrderFactory(email='')
        self.url = reverse('redirect3', kwargs={'reference': self.order.reference})

    def test_redirection_page(self):
        self.order.email = ''
        self.order.save()
        with self.assertRaises(NotImplementedError):
            response = self.app.get(self.url)


class ConfirmationView(AdyenSigMixin, WebTest):
    def setUp(self):
        self.order = OrderFactory()
        self.url = reverse('confirm')

        self.params = {
            'merchantReturnData': 'test',
            'paymentMethod': 'ideal',
            'reason': 'test',
            'shopperLocale': 'test',
            'skinCode': 'test',
            'merchantReference': self.order.reference
        }

    def test_empty_get(self):
        with self.assertRaises(AppError):
            self.app.get(self.url)

    def test_wrong_signature_response(self):
        params = {
            'merchantReference': self.order.reference
        }
        response = self.app.get(self.url, params=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '\n    Success!\n\n')

    def test_error_response(self):
        self.params['authResult'] = 'ERROR'
        params = self.sign_params(self.params)
        response = self.app.get(self.url, params=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '\n    Success!\n\n')

    def test_cancelled_response(self):
        self.params['authResult'] = 'CANCELLED'
        params = self.sign_params(self.params)
        response = self.app.get(self.url, params=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '\n    Success!\n\n')

    def test_refused_response(self):
        self.params['authResult'] = 'REFUSED'
        params = self.sign_params(self.params)
        response = self.app.get(self.url, params=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '\n    Success!\n\n')

    def test_pending_response(self):
        self.params['authResult'] = 'PENDING'
        params = self.sign_params(self.params)
        response = self.app.get(self.url, params=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '\n    Success!\n\n')

    def test_authorised_response(self):
        self.params['authResult'] = 'AUTHORISED'
        params = self.sign_params(self.params)
        response = self.app.get(self.url, params=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '\n    Success!\n\n')

    def test_other_response(self):
        self.params['authResult'] = 'OTHER'
        params = self.sign_params(self.params)
        response = self.app.get(self.url, params=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '\n    Success!\n\n')

    def test_post(self):
        self.params['authResult'] = 'AUTHORISED'
        params = self.sign_params(self.params)
        response = self.app.post(self.url, params=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '\n    Success!\n\n')

    def test_psp_reference(self):
        self.params['pspReference'] = 'reference'
        params = self.sign_params(self.params)
        response = self.app.post(self.url, params=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '\n    Success!\n\n')


class Confirmation2View(AdyenSigMixin, WebTest):
    def setUp(self):
        self.order = OrderFactory()
        self.url = reverse('confirm2')

        self.params = {
            'merchantReturnData': 'test',
            'paymentMethod': 'ideal',
            'reason': 'test',
            'shopperLocale': 'test',
            'skinCode': 'test',
            'merchantReference': self.order.reference,
            'pspReference': 'reference'
        }

    def test_empty_get(self):
        with self.assertRaises(NotImplementedError):
            self.app.get(self.url)

    def test_wrong_signature_response(self):
        params = {
            'merchantReference': self.order.reference
        }
        with self.assertRaises(NotImplementedError):
            self.app.get(self.url, params=params)

    def test_error_response(self):
        self.params['authResult'] = 'ERROR'
        params = self.sign_params(self.params)
        with self.assertRaises(NotImplementedError):
            self.app.get(self.url, params=params)

    def test_cancelled_response(self):
        self.params['authResult'] = 'CANCELLED'
        params = self.sign_params(self.params)
        with self.assertRaises(NotImplementedError):
            self.app.get(self.url, params=params)

    def test_refused_response(self):
        self.params['authResult'] = 'REFUSED'
        params = self.sign_params(self.params)
        with self.assertRaises(NotImplementedError):
            self.app.get(self.url, params=params)

    def test_pending_response(self):
        self.params['authResult'] = 'PENDING'
        params = self.sign_params(self.params)
        with self.assertRaises(NotImplementedError):
            self.app.get(self.url, params=params)

    def test_authorised_response(self):
        self.params['authResult'] = 'AUTHORISED'
        params = self.sign_params(self.params)
        with self.assertRaises(NotImplementedError):
            self.app.get(self.url, params=params)

    def test_other_response(self):
        self.params['authResult'] = 'OTHER'
        params = self.sign_params(self.params)
        with self.assertRaises(NotImplementedError):
            self.app.get(self.url, params=params)


class Confirmation3View(AdyenSigMixin, WebTest):
    def setUp(self):
        self.url = reverse('confirm3')

    def test_empty_get(self):
        self.app.get(self.url)
