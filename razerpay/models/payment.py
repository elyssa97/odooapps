from odoo import fields, models, api, _
import hashlib
from odoo.exceptions import ValidationError


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(
        string='Provider',
        selection_add=[("razerpay", "Razerpay")], ondelete={"razerpay": "set default"})
    merchant_name = fields.Char(
        string='Merchant Name',
        required=False)
    razerpay_key_id = fields.Char(
        string='Key ID', required_if_provider="razerpay",
        groups="base.group_user")
    razerpay_key_secret = fields.Char(
        string='Key secret', required_if_provider="razerpay",
        groups="base.group_user")

    def _get_default_payment_method_id(self):
        self.ensure_one()
        if self.provider != 'razerpay':
            return super()._get_default_payment_method_id()
        return self.env.ref('payment_razerpay.payment_method_razerpay').id


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    def _get_razerpay_url(self):
        if self.acquirer_id.state == 'test':
            return 'https://sandbox.merchant.razer.com'
        else:
            return 'https://pay.merchant.razer.com'

    def _get_specific_processing_values(self, processing_values):
        res = super()._get_specific_processing_values(processing_values)
        if self.provider != 'razerpay':
            return res
        md5_str = f'{self.amount}{self.acquirer_id.merchant_name}{self.reference}{self.acquirer_id.razerpay_key_id}'.encode(
            'utf-8')
        return {
            'tx_url': f'{self._get_razerpay_url()}/RMS/pay/{self.acquirer_id.merchant_name}/',
            'country': self.partner_id.country_id.code,
            'bill_name': self.partner_id.name,
            'bill_email': self.partner_id.email,
            'bill_mobile': self.partner_id.phone,
            'vcode': hashlib.md5(md5_str).hexdigest()
        }

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider != 'razerpay':
            return res
        return processing_values

    @api.model
    def _get_tx_from_feedback_data(self, provider, data):
        """ Override of payment to find the transaction based on Stripe data.

        :param str provider: The provider of the acquirer that handled the transaction
        :param dict data: The feedback data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if inconsistent data were received
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_feedback_data(provider, data)
        if provider != 'razerpay':
            return tx
        # $key0 = md5( $tranID.$orderid.$status.$domain.$amount.$currency );
        # $key1 = md5( $paydate.$domain.$key0.$appcode.$vkey );
        tx = self.search([('reference', '=', data.get('orderid')), ('provider', '=', 'razerpay')])
        if not tx:
            raise ValidationError(
                "Razerpay: " + _("No transaction found matching reference %s.", data.get('orderid'))
            )
        key_first = f"{data.get('tranID')}{data.get('orderid')}{data.get('status')}{data.get('domain')}{data.get('amount')}{data.get('currency')}".encode(
            'utf-8')

        key0 = hashlib.md5(key_first).hexdigest()
        key_second = f"{data.get('paydate')}{data.get('domain')}{key0}{data.get('appcode')}{tx.acquirer_id.razerpay_key_secret}".encode(
            'utf-8')
        key1 = hashlib.md5(key_second).hexdigest()

        if data.get('skey') != key1:
            raise ValidationError("Razerpay: " + _("There is mismatch in skey"))
        return tx

    def _process_feedback_data(self, data):
        super()._process_feedback_data(data)
        if self.provider != 'razerpay':
            return
        status = data.get('status')
        self.acquirer_reference = data.get('tranId')

        if status == '00':
            self._set_done()
        else:  # 'failure'
            error_code = data.get('error_code')
            self._set_error(
                "Razerpay: " + _("The payment encountered an error with code %s\n%s" % (error_code, data.get('error_desc')))
            )


class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'

    @api.model
    def _get_payment_method_information(self):
        res = super()._get_payment_method_information()
        res['razerpay'] = {'mode': 'unique', 'domain': [('type', '=', 'bank')]}
        return res
