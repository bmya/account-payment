from odoo import api, fields, models


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def _create_payments(self):
        payments = super(AccountPaymentRegister, self)._create_payments()
        if self.env.context.get('create_single_payments'):
            for payment in payments.filtered(lambda p: p.payment_group_id):
                payment.payment_group_id.name = payment.name
        return payments
