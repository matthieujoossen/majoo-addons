# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    check_deposit_account_id = fields.Many2one('account.account', 'Account for Check Deposits',
                                               domain=[('reconcile', '=', True)])
