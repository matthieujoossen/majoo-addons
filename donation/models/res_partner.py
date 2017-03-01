# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.one
    @api.depends('donation_ids.partner_id')
    def _donation_count(self):
        # The current user may not have access rights for donations
        try:
            self.donation_count = len(self.donation_ids)
        except:
            self.donation_count = 0

    donation_ids = fields.One2many('donation.donation', 'partner_id', string='Donations')
    donation_count = fields.Integer(compute='_donation_count', string="# of Donations", readonly=True)
    is_donor = fields.Boolean('Is Donor')
