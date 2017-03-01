# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class AccountCheckDeposit(models.Model):
    _name = "account.check.deposit"
    _description = "Account Check Deposit"
    _order = 'deposit_date desc'

    @api.model
    def _get_default_company(self):
        return self.env.user.company_id

    @api.model
    def _get_default_receipt_account(self):
        return self.env.user.company_id.check_deposit_account_id

    @api.multi
    @api.depends('company_id', 'company_id.currency_id', 'currency_id', 'check_payment_line_ids',
                 'check_payment_line_ids.amount_currency', 'check_payment_line_ids.debit',
                 'check_payment_line_ids.full_reconcile_id', 'move_id')
    def _compute_check_deposit(self):
        for deposit in self:
            deposit.total_amount = 0.0
            deposit.check_count = 0
            deposit.is_reconcile = False
            deposit.currency_none_same_company_id = False
            if deposit.company_id.currency_id != deposit.currency_id:
                deposit.currency_none_same_company_id = deposit.currency_id
            deposit.check_count = len(deposit.check_payment_line_ids)
            lines = deposit.check_payment_line_ids.mapped('move_line_id')
            if deposit.currency_none_same_company_id:
                deposit.total_amount = sum(lines.mapped('amount_currency'))
            else:
                deposit.total_amount = sum(lines.mapped('debit'))
            lines = deposit.move_id.line_ids
            deposit.is_reconcile = lines.filtered(lambda l: l.debit > 0 and l.full_reconcile_id) and True or False

    name = fields.Char('Name', size=64, readonly=True, index=True, default='/')
    check_payment_line_ids = fields.One2many('account.check.deposit.line', 'check_deposit_id', 'Check Payments',
                                             readonly=True, states={'draft': [('readonly', '=', False)]})
    deposit_date = fields.Date('Deposit Date', required=True, states={'done': [('readonly', '=', True)]},
                               default=fields.Date.today())
    journal_id = fields.Many2one('account.journal', 'Deposit Journal', domain=[('type', '=', 'bank')], required=True,
                                 readonly=True, states={'draft': [('readonly', '=', False)]})
    journal_default_account_id = fields.Many2one('account.account', related='journal_id.default_debit_account_id',
                                                 string='Default Debit Account of the Journal')
    receipt_account_id = fields.Many2one('account.account', 'Receipt Account', domain=[('reconcile', '=', True)],
                                         default=_get_default_receipt_account, required=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, readonly=True,
                                  states={'draft': [('readonly', '=', False)]})
    currency_none_same_company_id = fields.Many2one('res.currency', compute='_compute_check_deposit',
                                                    string='Currency (False if same as company)')
    state = fields.Selection([('draft', 'Draft'), ('deposit', 'Deposit'), ('done', 'Cash')], 'Status', readonly=True,
                             default='draft')
    move_id = fields.Many2one('account.move', 'Journal Entry', readonly=True)
    partner_bank_id = fields.Many2one('res.partner.bank', 'Bank Account', required=True, readonly=True,
                                      domain="[('company_id', '=', company_id)]",
                                      states={'draft': [('readonly', '=', False)]})
    line_ids = fields.One2many('account.move.line', related='move_id.line_ids', string='Lines', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, default=_get_default_company, readonly=True,
                                 states={'draft': [('readonly', '=', True)]})
    total_amount = fields.Monetary(compute='_compute_check_deposit', string="Total Amount", readonly=True)
    check_count = fields.Integer(compute='_compute_check_deposit', readonly=True, string="Number of Checks")
    is_reconcile = fields.Boolean(compute='_compute_check_deposit', readonly=True, string="Reconcile", type="boolean")

    @api.multi
    def _check_deposit(self):
        for deposit in self:
            deposit_currency = deposit.currency_id
            if deposit_currency == deposit.company_id.currency_id:
                # for line in deposit.check_payment_ids:
                for line in deposit.check_payment_line_ids:
                    move_line = line.move_line_id
                    if line.currency_id:
                        raise UserError(
                            _('Error:'),
                            _("The check with amount %s and reference '%s' is in currency %s but the deposit is in "
                              "currency %s.") % (
                                  move_line.debit, move_line.ref or '',
                                  move_line.company_currency_id.name,
                                  deposit_currency.name))
            else:
                # for line in deposit.check_payment_ids:
                for line in deposit.check_payment_line_ids:
                    move_line = line.move_line_id
                    if line.currency_id != deposit_currency:
                        raise UserError(
                            _('Error:'),
                            _("The check with amount %s and reference '%s' "
                              "is in currency %s but the deposit is in "
                              "currency %s.") % (
                                  move_line.debit, move_line.ref or '',
                                  move_line.company_currency_id.name,
                                  deposit_currency.name))
        return True

    _constraints = [(
        _check_deposit,
        "All the checks of the deposit must be in the currency of the deposit",
        # ['currency_id', 'check_payment_ids', 'company_id']
        ['currency_id', 'check_payment_line_ids', 'company_id']
        )]

    @api.multi
    def unlink(self):
        for deposit in self:
            if deposit.state == 'done':
                raise UserError(_('Error!'),
                                _("The deposit '%s' is in valid state, so you must cancel it before deleting it.")
                                % deposit.name)
        return super(AccountCheckDeposit, self).unlink()

    @api.multi
    def backtodraft(self):
        for deposit in self:
            if deposit.move_id:
                # It will raise here if journal_id.update_posted = False
                deposit.move_id.button_cancel()
                # for line in deposit.check_payment_ids:
                for line in deposit.check_payment_line_ids:
                    if line.full_reconcile_id:
                        line._full_reconcile_id.unlink()
                deposit.move_id.unlink()
            deposit.write({'state': 'draft'})
        return True

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].sudo().next_by_code('account.check.deposit')
        return super(AccountCheckDeposit, self).create(vals)

    @api.multi
    def _prepare_account_move_vals(self):
        self.ensure_one()
        move_vals = {'journal_id': self.journal_id.id,
                     'date': self.deposit_date,
                     'name': _('Check Deposit %s') % self.name,
                     'ref': self.name, }
        return move_vals

    @api.multi
    def _prepare_counterpart_move_lines_vals(self, total_debit, total_amount_currency):
        self.ensure_one()
        return {'name': _('Check Deposit %s') % self.name,
                'debit': total_debit,
                'credit': 0.0,
                'account_id': self.receipt_account_id.id,
                'partner_id': False,
                'currency_id': self.currency_none_same_company_id.id,
                'amount_currency': total_amount_currency, }

    @api.multi
    def prepare_deposit(self):
        self.ensure_one()
        if not self.check_payment_line_ids:
            raise UserError(_('You cannot have an empty deposit'))
        deposit_move_line_ids = self.check_payment_line_ids.mapped('move_line_id')
        if deposit_move_line_ids.filtered(lambda l: l.check_deposit_id):
            raise UserError(_('Some lines are already used. Please click on "Get Check to Deposit" to update list'))
        self.write({'state': 'deposit'})
        self.check_payment_line_ids.mapped('move_line_id').write({'check_deposit_id': self.id})

    @api.multi
    def validate_deposit(self):
        am_obj = self.env['account.move']
        aml_obj = self.env['account.move.line']
        for deposit in self:
            if deposit.state != 'deposit':
                raise UserError(_('You cannot validate deposit if state is different than "deposit"'))
            if not deposit.check_payment_line_ids:
                raise UserError(_('You cannot have an empty deposit'))
            move_vals = self._prepare_account_move_vals()
            self = self.with_context(journal_id=move_vals['journal_id'])
            move_id = am_obj.create(move_vals)
            total_debit = 0.0
            total_amount_currency = 0.0
            to_reconcile_line_ids = []
            for line in deposit.check_payment_line_ids:
                total_debit += line.debit
                total_amount_currency += line.amount_currency
                line_vals = line.move_line_id._prepare_check_deposit_move_line_vals()
                line_vals['move_id'] = move_id.id
                move_line_id = aml_obj.with_context(check_move_validity=False).create(line_vals)
                to_reconcile_line_ids.append(line.move_line_id | move_line_id)

            # Create counter-part
            if not deposit.receipt_account_id:
                raise UserError(_("""Configuration Error: Missing Account for Check Deposits."""))

            counter_vals = deposit._prepare_counterpart_move_lines_vals(total_debit, total_amount_currency)
            counter_vals['move_id'] = move_id.id
            aml_obj.create(counter_vals)

            move_id.post()
            deposit.write({'state': 'done', 'move_id': move_id.id})
            # We have to reconcile after post()
            for reconcile_line_ids in to_reconcile_line_ids:
                reconcile_line_ids.reconcile()
        return True

    @api.onchange('company_id')
    def onchange_company_id(self):
        if self.company_id:
            if self.currency_id:
                if self.company_id.currency_id == self.currency_id:
                    self.currency_none_same_company_id = False
                else:
                    self.currency_none_same_company_id = self.currency_id
            partner_bank_ids = self.env['res.partner.bank'].search([('company_id', '=', self.company_id.id)])
            if len(partner_bank_ids) == 1:
                self.partner_bank_id = partner_bank_ids
        else:
            self.currency_none_same_company_id = False
            self.partner_bank_id = False

    @api.onchange('journal_id')
    def onchange_journal_id(self):
        if self.journal_id:
            self.journal_default_account_id = self.journal_id.default_debit_account_id
            if self.journal_id.currency_id:
                self.currency_id = self.journal_id.currency_id
            else:
                self.currency_id = self.journal_id.company_id.currency_id
        else:
            self.journal_default_account_id = False

    @api.onchange('currency_id')
    def onchange_currency_id(self):
        if self.currency_id and self.company_id and self.company_id.currency_id != self.currency_id:
            self.currency_none_same_company_id = self.currency_id
        else:
            self.currency_none_same_company_id = False

    @api.multi
    def get_checks(self):
        self.ensure_one()
        self.check_payment_line_ids.unlink()
        line_domain = [('full_reconcile_id', '=', False),
                       ('debit', '>', 0),
                       ('check_deposit_id', '=', False),
                       ('currency_id', '=', self.currency_none_same_company_id.id),
                       ('account_id', '=', self.journal_default_account_id.id)]
        line_ids = self.env['account.move.line'].search(line_domain)
        for line in line_ids:
            self.env['account.check.deposit.line'].create({'check_deposit_id': self.id,
                                                           'move_line_id': line.id, })


class AccountCheckDepositLine(models.Model):
    _name = "account.check.deposit.line"
    _description = "Account Check Deposit Line"

    check_deposit_id = fields.Many2one('account.check.deposit', 'Check Deposit', ondelete='cascade', readonly=True,
                                       required=True)
    move_line_id = fields.Many2one('account.move.line', 'Move Line', ondelete='restrict', readonly=True, required=True)
    debit = fields.Monetary(related='move_line_id.debit', readonly=True)
    amount_currency = fields.Monetary(related='move_line_id.amount_currency', readonly=True)
    full_reconcile_id = fields.Many2one('account.full.reconcile', related='move_line_id.full_reconcile_id',
                                        readonly=True)
    partner_id = fields.Many2one('res.partner', related='move_line_id.partner_id', readonly=True)
    name = fields.Char('Check Reference')
    company_id = fields.Many2one('res.company', related='move_line_id.company_id')
    currency_id = fields.Many2one('res.currency', related='move_line_id.currency_id', readonly=True)
    company_currency_id = fields.Many2one('res.currency', related='move_line_id.company_currency_id', readonly=True)
    display_amount = fields.Monetary('Amount', compute='_get_amount')

    @api.multi
    @api.depends('amount_currency', 'debit')
    def _get_amount(self):
        for line in self:
            line.display_amount = line.debit > line.amount_currency and line.debit or line.amount_currency
