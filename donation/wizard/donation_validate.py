# -*- encoding: utf-8 -*-

from odoo import models, api


class DonationValidate(models.TransientModel):
    _name = 'donation.validate'
    _description = 'Validate Donations'

    @api.one
    def run(self):
        assert self.env.context.get('active_model') == 'donation.donation', 'Source model must be donations'
        assert self.env.context.get('active_ids'), 'No donations selected'
        donations = self.env['donation.donation'].browse(self.env.context.get('active_ids'))
        donations.validate()
        return
