# -*- coding: utf-8 -*-

from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    # begin with context_ to allow user to change it by himself
    context_donation_campaign_id = fields.Many2one('donation.campaign', string='Current Donation Campaign')
    context_donation_journal_id = fields.Many2one('account.journal', string='Current Donation Payment Method',
                                                  domain=[('type', 'in', ('bank', 'cash')),
                                                          ('allow_donation', '=', True)], company_dependent=True)
