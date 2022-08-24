import json

from odoo import http
from odoo.http import request


class Razerpay(http.Controller):


    @http.route('/payment/razerpay/validate', type='http', auth='public', csrf=False)
    def razerpay_return_from_validation(self, **data):
        """ Process the data returned by Stripe after redirection for validation.

        :param dict data: The GET params appended to the URL in `_stripe_create_checkout_session`
        """
        # Retrieve the acquirer based on the tx reference included in the return url
        print(data)
        acquirer_sudo = request.env['payment.transaction'].sudo()._get_tx_from_feedback_data(
            'razerpay', data
        ).acquirer_id
        # Handle the feedback data crafted with Stripe API objects
        request.env['payment.transaction'].sudo()._handle_feedback_data('razerpay', data)

        # Redirect the user to the status page
        return request.redirect('/payment/status')
