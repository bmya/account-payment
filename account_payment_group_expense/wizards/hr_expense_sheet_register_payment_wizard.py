from odoo import models


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    def expense_post_payment(self):
        """ Update context in order to identify when a account.payment is
        created from an expense.
        """
        return super(
            AccountPaymentRegister,
            self.with_context(create_from_expense=True)
        ).action_create_payments()
