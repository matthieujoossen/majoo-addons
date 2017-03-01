# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class DonationDonation(models.Model):
    _name = 'donation.donation'
    _description = 'Donation'
    _order = 'id desc'
    # _rec_name = 'display_name'
    _inherit = ['mail.thread']

    @api.one
    @api.depends('line_ids', 'line_ids.unit_price', 'line_ids.quantity', 'donation_date', 'currency_id', 'company_id')
    def _compute_total(self):
        total = 0.0
        for line in self.line_ids:
            total += line.quantity * line.unit_price
        self.amount_total = total
        donation_currency = self.currency_id.with_context(date=self.donation_date)
        total_company_currency = donation_currency.compute(total, self.company_id.currency_id)
        self.amount_total_company_currency = total_company_currency

    # We don't want a depends on partner_id.country_id, because if the partner we want to keep the old country for past
    # donations
    @api.one
    @api.depends('partner_id')
    def _compute_country_id(self):
        self.sudo().country_id = self.partner_id.country_id or False

    @api.model
    def _default_currency(self):
        company_id = self.env['res.company']._company_default_get('donation.donation')
        return company_id.currency_id

    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  states={'done': [('readonly', True)]}, track_visibility='onchange',
                                  ondelete='restrict', default=_default_currency)
    partner_id = fields.Many2one('res.partner', string='Donor', required=True, states={'done': [('readonly', True)]},
                                 track_visibility='onchange', ondelete='restrict')
    country_id = fields.Many2one('res.country', string='Country', compute='_compute_country_id', store=True,
                                 readonly=True, copy=False)
    check_total = fields.Monetary(string='Check Amount', states={'done': [('readonly', True)]})
    amount_total = fields.Monetary(compute='_compute_total', string='Amount Total', store=True, readonly=True)
    amount_total_company_currency = fields.Monetary(compute='_compute_total', string='Amount Total in Company Currency',
                                                    store=True, readonly=True)
    donation_date = fields.Date(string='Donation Date', required=True, states={'done': [('readonly', True)]},
                                track_visibility='onchange')
    company_id = fields.Many2one('res.company', string='Company', required=True, states={'done': [('readonly', True)]},
                                 default=lambda self: self.env['res.company']._company_default_get('donation.donation'))
    line_ids = fields.One2many('donation.line', 'donation_id', string='Donation Lines',
                               states={'done': [('readonly', True)]}, copy=True)
    move_id = fields.Many2one('account.move', string='Account Move', readonly=True, copy=False)
    number = fields.Char(related='move_id.name', readonly=True, size=64, store=True, string='Donation Number')
    journal_id = fields.Many2one('account.journal', string='Payment Method', required=True,
                                 domain=[('type', 'in', ('bank', 'cash')), ('allow_donation', '=', True)],
                                 states={'done': [('readonly', True)]}, track_visibility='onchange',
                                 default=lambda self: self.env.user.context_donation_journal_id)
    payment_ref = fields.Char(string='Payment Reference', size=32, states={'done': [('readonly', True)]})
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done'), ('cancel', 'Cancelled')], string='State',
                             readonly=True, copy=False, default='draft', track_visibility='onchange')
    company_currency_id = fields.Many2one(related='company_id.currency_id', string="Company Currency", readonly=True)
    campaign_id = fields.Many2one('donation.campaign', string='Donation Campaign', track_visibility='onchange',
                                  ondelete='restrict', default=lambda self: self.env.user.context_donation_campaign_id)
    display_name = fields.Char(string='Display Name', compute='_compute_display_name', readonly=True, store=True,
                               index=True)

    @api.one
    @api.constrains('donation_date')
    def _check_donation_date(self):
        if self.donation_date > fields.Date.context_today(self):
            raise UserError(_('The date of the donation of %s should be today or in the past, not in the future!')
                            % self.partner_id.name)

    @api.model
    def _prepare_move_line_name(self):
        return _('Donation of %s') % self.partner_id.name

    @api.model
    def _prepare_donation_move(self):
        if not self.journal_id.default_debit_account_id:
            raise UserError(_("Missing Default Debit Account on journal '%s'.") % self.journal_id.name)
        movelines = []
        currency_id = self.company_id.currency_id.id != self.currency_id.id and self.currency_id.id or False
        amount_total_company_cur = 0.0
        total_amount_currency = 0.0
        name = self._prepare_move_line_name()

        aml = {}
        for donation_line in self.line_ids:
            if donation_line.in_kind:
                continue
            amount_total_company_cur += donation_line.amount_company_currency
            account_id = donation_line.product_id.property_account_income_id.id
            if not account_id:
                account_id = donation_line.product_id.categ_id.property_account_income_categ.id
            if not account_id:
                raise UserError(_("Missing income account on product '%s' or on it's related product category")
                                % donation_line.product_id.name)
            analytic_account_id = donation_line.get_analytic_account_id()
            amount_currency = 0.0
            if donation_line.amount_company_currency > 0:
                credit = donation_line.amount_company_currency
                debit = 0
                amount_currency = donation_line.amount * -1
            else:
                debit = donation_line.amount_company_currency * -1
                credit = 0
                amount_currency = donation_line.amount
            if (account_id, analytic_account_id) in aml:
                aml[(account_id, analytic_account_id)]['credit'] += credit
                aml[(account_id, analytic_account_id)]['debit'] += debit
                aml[(account_id, analytic_account_id)]['amount_currency'] += amount_currency
            else:
                aml[(account_id, analytic_account_id)] = {
                    'credit': credit,
                    'debit': debit,
                    'amount_currency': amount_currency,
                    }
        if not aml:
            return False

        for (account_id, analytic_account_id), content in aml.iteritems():
            movelines.append((0, 0, {
                'name': name,
                'credit': content['credit'],
                'debit': content['debit'],
                'account_id': account_id,
                'analytic_account_id': analytic_account_id,
                'partner_id': self.partner_id.id,
                'currency_id': currency_id,
                'amount_currency': (currency_id and content['amount_currency'] or 0.0),
                }))

        # counter-part
        if amount_total_company_cur > 0:
            debit = amount_total_company_cur
            credit = 0
            total_amount_currency = self.amount_total
        else:
            credit = amount_total_company_cur * -1
            debit = 0
            total_amount_currency = self.amount_total * -1
        movelines.append(
            (0, 0, {
                'debit': debit,
                'credit': credit,
                'name': name,
                'account_id': self.journal_id.default_debit_account_id.id,
                'partner_id': self.partner_id.id,
                'currency_id': currency_id,
                'amount_currency': (currency_id and total_amount_currency or 0.0),
            }))

        vals = {
            'journal_id': self.journal_id.id,
            'date': self.donation_date,
            'ref': self.payment_ref,
            'line_ids': movelines,
            }
        return vals

    @api.one
    def validate(self):
        if not self.line_ids:
            raise UserError(_("Cannot validate the donation of %s because it doesn't have any lines!") %
                            self.partner_id.name)
        if self.state != 'draft':
            raise UserError(_("Cannot validate the donation of %s because it is not in draft state.") %
                            self.partner_id.name)
        check_group = 'account.group_supplier_inv_check_total'
        if (self.env['res.users'].has_group(check_group) and self.check_total != self.amount_total):
            raise UserError(
                _("The amount of the donation of %s (%s) is different from the sum of the donation lines (%s).") %
                (self.partner_id.name, self.check_total, self.amount_total))

        donation_write_vals = {'state': 'done'}
        if self.amount_total:
            move_vals = self._prepare_donation_move()
            if move_vals:
                move = self.env['account.move'].create(move_vals)
                move.post()
                donation_write_vals['move_id'] = move.id
            else:
                self.message_post(_('Full in-kind donation: no account move generated'))
        self.write(donation_write_vals)
        return

    @api.one
    def save_default_values(self):
        vals = {'context_donation_journal_id': self.journal_id.id,
                'context_donation_campaign_id': self.campaign_id.id, }
        self.env.user.write(vals)
        return

    @api.one
    def done2cancel(self):
        '''from Done state to Cancel state'''
        if self.move_id:
            self.move_id.button_cancel()
            self.move_id.unlink()
        self.state = 'cancel'
        return

    @api.one
    def cancel2draft(self):
        '''from Cancel state to Draft state'''
        if self.move_id:
            raise UserError(_("A cancelled donation should not be linked to an account move"))
        self.state = 'draft'
        return

    @api.multi
    def unlink(self):
        for donation in self:
            if donation.state == 'done':
                raise UserError(_("The donation '%s' is in Done state, so you cannot delete it.") % donation.number)
            if donation.move_id:
                raise UserError(_("The donation '%s' is linked to an account move, so you cannot delete it."))
        return super(DonationDonation, self).unlink()

    @api.depends('state', 'partner_id', 'partner_id.name', 'number')
    def _compute_display_name(self):
        for donation in self:
            if self.state == 'draft':
                name = _('Draft Donation of %s') % donation.partner_id.name
            elif self.state == 'cancel':
                name = _('Cancelled Donation of %s') % donation.partner_id.name
            else:
                name = donation.number
            donation.display_name = name


class DonationLine(models.Model):
    _name = 'donation.line'
    _description = 'Donation Lines'
    _rec_name = 'product_id'

    @api.one
    @api.depends('unit_price', 'quantity')
    def _compute_amount(self):
        self.amount = self.quantity * self.unit_price

    @api.one
    @api.depends('unit_price', 'quantity', 'donation_id.currency_id', 'donation_id.donation_date',
                 'donation_id.company_id')
    def _compute_amount_company_currency(self):
        amount = self.quantity * self.unit_price
        donation_currency = self.donation_id.currency_id.with_context(date=self.donation_id.donation_date)
        self.amount_company_currency = donation_currency.compute(amount, self.donation_id.company_id.currency_id)

    donation_id = fields.Many2one('donation.donation', string='Donation', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True, domain=[('donation', '=', True)],
                                 ondelete='restrict')
    quantity = fields.Integer(string='Quantity', default=1)
    unit_price = fields.Monetary(string='Unit Price')
    amount = fields.Monetary(compute='_compute_amount', string='Amount', store=True)
    currency_id = fields.Many2one('res.currency', related='donation_id.currency_id')
    amount_company_currency = fields.Monetary(compute='_compute_amount_company_currency',
                                              string='Amount in Company Currency', store=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account',
                                          domain=[('type', 'not in', ('view', 'template'))], ondelete='restrict')
    in_kind = fields.Boolean(string='In Kind')
    sequence = fields.Integer('Sequence')

    @api.onchange('product_id')
    def product_id_change(self):
        if self.product_id:
            if self.product_id.list_price:
                self.unit_price = self.product_id.list_price
            self.in_kind = self.product_id.in_kind_donation

    @api.model
    def get_analytic_account_id(self):
        return self.analytic_account_id.id or False
