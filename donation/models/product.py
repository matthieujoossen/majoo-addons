# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    donation = fields.Boolean(string='Is a Donation', help="Specify if the product can be selected in a donation line.")
    in_kind_donation = fields.Boolean(string="In-Kind Donation")

    @api.onchange('donation')
    def _donation_change(self):
        if self.donation:
            self.type = 'service'
            self.sale_ok = False

    @api.onchange('in_kind_donation')
    def _in_kind_donation_change(self):
        if self.in_kind_donation:
            self.donation = True


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.onchange('donation')
    def _donation_change(self):
        if self.donation:
            self.type = 'service'
            self.sale_ok = False

    @api.onchange('in_kind_donation')
    def _in_kind_donation_change(self):
        if self.in_kind_donation:
            self.donation = True
