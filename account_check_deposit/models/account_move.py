# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    check_deposit_id = fields.Many2one('account.check.deposit', 'Check Deposit')

    @api.multi
    def _prepare_check_deposit_move_line_vals(self):
        self.ensure_one()
        assert (self.debit > 0), 'Debit must have a value'
        return {'name': _('Check Deposit - Ref. Check %s') % self.ref,
                'credit': self.debit,
                'debit': 0.0,
                'account_id': self.account_id.id,
                'partner_id': self.partner_id.id,
                'currency_id': self.currency_id.id or False,
                'amount_currency': self.amount_currency * -1, }
