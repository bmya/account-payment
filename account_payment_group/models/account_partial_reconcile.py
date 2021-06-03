from odoo import api, fields, models


class AccountPartialReconcile(models.Model):
    _inherit = 'account.partial.reconcile'

    payment_group_id = fields.Many2one('account.payment.group')

