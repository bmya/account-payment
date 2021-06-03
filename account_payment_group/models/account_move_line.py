# © 2016 ADHOC SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
# from odoo.exceptions import UserError, ValidationError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # inverse field of the one created on payment groups, used by other modules
    # like sipreco

    amount_parcial = fields.Float('Monto a cancelar', copy=False)

    payment_group_ids = fields.Many2many(
        'account.payment.group',
        'account_move_line_payment_group_to_pay_rel',
        'to_pay_line_id',
        'payment_group_id',
        string="Payment Groups",
        readonly=True,
        copy=False,
        # auto_join not yet implemented for m2m. TODO enable when implemented
        # https://github.com/odoo/odoo/blob/master/odoo/osv/expression.py#L899
        # auto_join=True,
    )

    @api.multi
    def _compute_payment_group_matched_amount(self):
        """
        Reciviendo un payment_group_id por contexto, decimos en ese payment
        group, cuanto se pago para la lína en cuestión.
        """
        payment_group_id = self._context.get('payment_group_id')
        if not payment_group_id:
            return False
        payments = self.env['account.payment.group'].browse(
            payment_group_id).payment_ids
        payment_move_lines = payments.mapped('move_line_ids')

        for rec in self:
            matched_amount = 0.0
            reconciles = self.env['account.partial.reconcile'].search([
                ('credit_move_id', 'in', payment_move_lines.ids),
                ('debit_move_id', '=', rec.id)])
            matched_amount += sum(reconciles.mapped('amount'))

            reconciles = self.env['account.partial.reconcile'].search([
                ('debit_move_id', 'in', payment_move_lines.ids),
                ('credit_move_id', '=', rec.id)])
            matched_amount -= sum(reconciles.mapped('amount'))
            rec.payment_group_matched_amount = matched_amount

    payment_group_matched_amount = fields.Monetary(
        compute='_compute_payment_group_matched_amount',
        currency_field='company_currency_id',
    )

    @api.multi
    def _reconcile_lines(self, debit_moves, credit_moves, field):
        """ This function loops on the 2 recordsets given as parameter as long as it
            can find a debit and a credit to reconcile together. It returns the recordset of the
            account move lines that were not reconciled during the process.
        """
        (debit_moves + credit_moves).read([field])
        to_create = []
        cash_basis = debit_moves and debit_moves[0].account_id.internal_type in ('receivable', 'payable') or False
        cash_basis_percentage_before_rec = {}
        dc_vals = {}
        while (debit_moves and credit_moves):
            debit_move = debit_moves[0]
            credit_move = credit_moves[0]
            company_currency = debit_move.company_id.currency_id
            # We need those temporary value otherwise the computation might be wrong below
            temp_amount = -credit_move.amount_residual
            recon_amount = -credit_move[field]
            if debit_move.amount_parcial > 0:
                temp_amount = debit_move.amount_parcial if debit_move.amount_parcial < -credit_move.amount_residual else -credit_move.amount_residual
                recon_amount = debit_move.amount_parcial if debit_move.amount_parcial < -credit_move[field] else -credit_move[field]
            if credit_move.amount_parcial > 0:
                temp_amount = credit_move.amount_parcial if credit_move.amount_parcial < debit_move.amount_residual else debit_move.amount_residual
                recon_amount = credit_move.amount_parcial if credit_move.amount_parcial < debit_move[field] else debit_move[field]
            temp_amount_residual = min(debit_move.amount_residual, temp_amount)
            temp_amount_residual_currency = min(debit_move.amount_residual_currency, -credit_move.amount_residual_currency)
            dc_vals[(debit_move.id, credit_move.id)] = (debit_move, credit_move, temp_amount_residual_currency)
            amount_reconcile = min(debit_move[field], recon_amount)

            # Remove from recordset the one(s) that will be totally reconciled
            # For optimization purpose, the creation of the partial_reconcile are done at the end,
            # therefore during the process of reconciling several move lines, there are actually no recompute performed by the orm
            # and thus the amount_residual are not recomputed, hence we have to do it manually.
            if debit_move.amount_parcial > 0:
                if debit_move.amount_parcial <= -credit_move.amount_residual:
                    debit_move.amount_parcial = 0
                    debit_moves -= debit_move
                    credit_moves[0].amount_residual += temp_amount_residual
                else:
                    credit_move.amount_parcial = 0
                    credit_moves -= credit_move
                    debit_moves[0].amount_parcial -= temp_amount_residual
                    debit_moves[0].amount_residual -= temp_amount_residual
            elif credit_move.amount_parcial > 0:
                if credit_move.amount_parcial <= debit_move.amount_residual:
                    credit_move.amount_parcial = 0
                    credit_moves -= credit_move
                    debit_moves[0].amount_residual -= temp_amount_residual
                else:
                    debit_move.amount_parcial = 0
                    debit_moves -= debit_move
                    credit_moves[0].amount_parcial -= temp_amount_residual
                    credit_moves[0].amount_residual += temp_amount_residual
            else:
                if amount_reconcile == debit_move[field]:
                    debit_moves -= debit_move
                else:
                    debit_moves[0].amount_residual -= temp_amount_residual
                    debit_moves[0].amount_residual_currency -= temp_amount_residual_currency

                if amount_reconcile == -credit_move[field]:
                    credit_moves -= credit_move
                else:
                    credit_moves[0].amount_residual += temp_amount_residual
                    credit_moves[0].amount_residual_currency += temp_amount_residual_currency
            # Check for the currency and amount_currency we can set
            currency = False
            amount_reconcile_currency = 0
            if field == 'amount_residual_currency':
                currency = credit_move.currency_id.id
                amount_reconcile_currency = temp_amount_residual_currency
                amount_reconcile = temp_amount_residual
            elif bool(debit_move.currency_id) != bool(credit_move.currency_id):
                # If only one of debit_move or credit_move has a secondary currency, also record the converted amount
                # in that secondary currency in the partial reconciliation. That allows the exchange difference entry
                # to be created, in case it is needed. It also allows to compute the amount residual in foreign currency.
                currency = debit_move.currency_id or credit_move.currency_id
                currency_date = debit_move.currency_id and credit_move.date or debit_move.date
                amount_reconcile_currency = company_currency._convert(amount_reconcile, currency, debit_move.company_id,
                                                                      currency_date)
                currency = currency.id

            if cash_basis:
                tmp_set = debit_move | credit_move
                cash_basis_percentage_before_rec.update(tmp_set._get_matched_percentage())
            data = {
                'debit_move_id': debit_move.id,
                'credit_move_id': credit_move.id,
                'amount': amount_reconcile,
                'amount_currency': amount_reconcile_currency,
                'currency_id': currency,
            }
            if 'payment_group_id' in self._context:
                data['payment_group_id'] = self._context['payment_group_id']
            to_create.append(data)
        cash_basis_subjected = []
        part_rec = self.env['account.partial.reconcile']
        with self.env.norecompute():
            for partial_rec_dict in to_create:
                debit_move, credit_move, amount_residual_currency = dc_vals[
                    partial_rec_dict['debit_move_id'], partial_rec_dict['credit_move_id']]
                # /!\ NOTE: Exchange rate differences shouldn't create cash basis entries
                # i. e: we don't really receive/give money in a customer/provider fashion
                # Since those are not subjected to cash basis computation we process them first
                if not amount_residual_currency and debit_move.currency_id and credit_move.currency_id:
                    part_rec.create(partial_rec_dict)
                else:
                    cash_basis_subjected.append(partial_rec_dict)

            for after_rec_dict in cash_basis_subjected:
                new_rec = part_rec.create(after_rec_dict)
                # if the pair belongs to move being reverted, do not create CABA entry
                if cash_basis and not (new_rec.debit_move_id + new_rec.credit_move_id).mapped('move_id').mapped(
                        'reverse_entry_id'):
                    new_rec.create_tax_cash_basis_entry(cash_basis_percentage_before_rec)
        self.recompute()

        return debit_moves + credit_moves

    @api.multi
    def write(self, vals):
        for rec in self:
            if rec.move_id.state != 'posted':
                return super(AccountMoveLine, rec).write(vals)
            elif 'amount_parcial' in vals:
                return super(AccountMoveLine, rec).write(vals)

    @api.multi
    def remove_move_reconcile(self):
        """ Undo a reconciliation """
        if not self:
            return True
        rec_move_ids = self.env['account.partial.reconcile']
        for account_move_line in self:
            for invoice in account_move_line.payment_id.invoice_ids:
                if invoice.id == self.env.context.get(
                        'invoice_id') and account_move_line in invoice.payment_move_line_ids:
                    account_move_line.payment_id.write({'invoice_ids': [(3, invoice.id, None)]})
            rec_move_ids += account_move_line.matched_debit_ids
            rec_move_ids += account_move_line.matched_credit_ids
        if self.env.context.get('invoice_id'):
            current_invoice = self.env['account.invoice'].browse(self.env.context['invoice_id'])
            aml_to_keep = current_invoice.move_id.line_ids | current_invoice.move_id.line_ids.mapped(
                'full_reconcile_id.exchange_move_id.line_ids')
            rec_move_ids = rec_move_ids.filtered(
                lambda r: (r.debit_move_id + r.credit_move_id) & aml_to_keep
            )
        return rec_move_ids.unlink()
