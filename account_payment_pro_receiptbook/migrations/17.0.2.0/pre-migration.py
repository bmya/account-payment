from openupgradelib import openupgrade


_column_copy = {
    'account_payment': [
        ('payment_group_id', 'payment_group_id_bu', None),
    ],
}


_table_renames = [
    ('account_payment_group', 'account_payment_group_bu'),
    # ('account_payment_receiptbook', 'account_payment_receiptbook_bu'),
    ('account_move_line_payment_group_to_pay_rel', 'account_move_line_payment_group_to_pay_rel_bu'),
]


@openupgrade.migrate()
def migrate(env, version):
    # backup de columnas que nos interesan antes de que se borren
    openupgrade.copy_columns(env.cr, _column_copy)
    # backup de tables y checkbooks
    for old_table, new_table in _table_renames:
        if openupgrade.table_exists(env.cr, old_table) and not openupgrade.table_exists(env.cr, new_table):
            openupgrade.logged_query(
                env.cr, "CREATE TABLE %s AS SELECT * FROM %s" % (new_table, old_table))

    # lo movimos a ul 1026
    # # Add temporary table for avoiding the automatic launch of the compute method
    # openupgrade.logged_query(
    #     env.cr, "CREATE TABLE account_move_line_payment_to_pay_rel (payment_id integer, to_pay_line_id integer)",
    # )

    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_payment
        ADD COLUMN IF NOT EXISTS receiptbook_id int4
        """,
    )
