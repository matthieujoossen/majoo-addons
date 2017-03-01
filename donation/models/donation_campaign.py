# -*- coding: utf-8 -*-

from odoo import models, fields, api


class DonationCampaign(models.Model):
    _name = 'donation.campaign'
    _description = 'Code attributed for a Donation Campaign'
    _order = 'code'
    # _rec_name = 'display_name'

    @api.depends('code', 'name')
    def _compute_display_name(self):
        for campaign in self:
            name = campaign.code and u'[%s] %s' % (campaign.code, campaign.name) or campaign.name
            campaign.display_name = name

    code = fields.Char(string='Code', size=10)
    name = fields.Char(string='Name', required=True)
    display_name = fields.Char(string='Display Name', compute='_compute_display_name', readonly=True, store=True)
    start_date = fields.Date(string='Start Date', default=fields.Date.context_today)
    nota = fields.Text(string='Notes')
