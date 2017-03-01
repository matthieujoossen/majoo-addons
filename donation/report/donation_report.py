# -*- encoding: utf-8 -*-

from odoo import models, fields


class DonationReport(models.Model):
    _name = "donation.report"
    _description = "Donations Analysis"
    _auto = False
    _rec_name = 'donation_date'
    _order = "donation_date desc"

    donation_date = fields.Date(string='Donation Date', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Donor', readonly=True)
    country_id = fields.Many2one('res.country', string='Partner Country', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    currency_id = fields.Many2one('res.currency')
    product_categ_id = fields.Many2one('product.category', string='Category of Product', readonly=True)
    campaign_id = fields.Many2one('donation.campaign', string='Donation Campaign', readonly=True)
    in_kind = fields.Boolean(string='In Kind')
    amount_company_currency = fields.Monetary('Amount Company Currency', readonly=True)
    journal_id = fields.Many2one('account.journal', string='Journal', readonly=True)

    def _select(self):
        select = """
            SELECT min(l.id) AS id,
                d.donation_date AS donation_date,
                l.product_id AS product_id,
                l.in_kind AS in_kind,
                pt.categ_id AS product_categ_id,
                d.company_id AS company_id,
                d.partner_id AS partner_id,
                d.country_id AS country_id,
                d.campaign_id AS campaign_id,
                d.currency_id AS currency_id,
                d.journal_id AS journal_id,
                sum(l.amount_company_currency) AS amount_company_currency
                """
        return select

    def _from(self):
        from_sql = """
            donation_line l
                LEFT JOIN donation_donation d ON (d.id=l.donation_id)
                LEFT JOIN product_product pp ON (l.product_id=pp.id)
                LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
            """
        return from_sql

    def _where(self):
        where = """
            WHERE d.state='done'
            """
        return where

    def _group_by(self):
        group_by = """
            GROUP BY l.product_id,
                l.in_kind,
                pt.categ_id,
                d.donation_date,
                d.partner_id,
                d.country_id,
                d.campaign_id,
                d.company_id,
                d.currency_id,
                d.journal_id
            """
        return group_by

    def init(self):
        self.env.cr.execute("""
            DROP VIEW IF EXISTS %s;
            CREATE OR REPLACE VIEW %s AS (%s FROM %s %s %s)""" % (self._table, self._table, self._select(),
                                                                  self._from(), self._where(), self._group_by()))
