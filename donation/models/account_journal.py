# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    allow_donation = fields.Boolean(string='Donation Payment Method')

    @api.one
    @api.constrains('type', 'allow_donation')
    def _check_donation(self):
        if self.allow_donation and self.type not in ('bank', 'cash'):
            raise UserError(_("The journal '%s' has the option 'Donation Payment Method', "
                              "so it's type should be 'Cash' or 'Bank and Checks'.") % self.name)
