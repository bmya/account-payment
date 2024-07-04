from openupgradelib import openupgrade
import logging
_logger = logging.getLogger(__name__)


def migrate_payment_grup_note(env):
    query = "select ap.id, notes from account_payment_group_bu apg join account_payment as ap on ap.payment_group_id_bu = apg.id where notes is not null"
    openupgrade.logged_query(env.cr, query)
    res = env.cr.fetchall()
    for payment_id, note in res:
        env['account.payment'].browse(payment_id).message_post(body='Nota migrada desde payment group version anterior: %s' % note)


def migrate_payment_grup_data(env):

    # mover campos (excepto m2m)
    query = """
        update account_payment ap set
            unreconciled_amount = apg.unreconciled_amount,
            receiptbook_id = apg.receiptbook_id
        from account_payment_group_bu as apg
        where
            ap.payment_group_id_bu = apg.id
        """
    openupgrade.logged_query(env.cr, query)

    # popular to_pay_move_lines (m2m field, en post)
    query = """
        insert into account_move_line_payment_to_pay_rel (to_pay_line_id, payment_id)
        select
            rel.to_pay_line_id,  ap.id as payment_id
        from
            account_move_line_payment_group_to_pay_rel_bu rel
        join
            account_payment ap on ap.payment_group_id_bu = rel.payment_group_id
        """
    openupgrade.logged_query(env.cr, query)

    openupgrade.merge_models(env.cr, 'account.payment.group', 'account.payment', 'payment_group_id_bu')


@openupgrade.migrate()
def migrate(env, version):
    _logger.debug('Running migrate script for l10n_ar_withholding')
    migrate_payment_grup_data(env)
    migrate_payment_grup_note(env)
