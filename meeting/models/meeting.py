# -*- coding: utf-8 -*-

from datetime import datetime as dt

from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class MeetingType(models.Model):
    _name = 'meeting.type'

    name = fields.Char('Name')

    _sql_constraints = [
        ('meeting_type_name', "UNIQUE(name)", 'Meeting name must be unique!'),
    ]


class MeetingDecision(models.Model):
    _name = 'meeting.decision'
    _order = 'sequence'

    meeting_id = fields.Many2one('meeting.meeting', 'Meeting', ondelete='restrict', required=True)
    decision = fields.Char('Decision', required=True)
    result_vote = fields.Char('Result Vote', help='unanimity, 75%, ...', required=True)
    sequence = fields.Integer('Sequence', default=1)

    _sql_constraints = [
        ('meeting_decision_unicity', "UNIQUE(meeting_id, decision)", "Meeting decision must be unique per meeting"),
    ]


class MeetingMeeting(models.Model):
    _name = 'meeting.meeting'
    _inherit = ['pad.common']
    _description = 'Meeting'
    _order = 'date_begin desc'

    _pad_fields = ['pad_agenda', 'pad_report']

    @api.one
    @api.depends('date_begin', 'date_end')
    def _get_duration(self):
        if self.date_end and self.date_begin:
            begin = dt.strptime(self.date_begin, DEFAULT_SERVER_DATETIME_FORMAT)
            end = dt.strptime(self.date_end, DEFAULT_SERVER_DATETIME_FORMAT)
            self.duration = str(end - begin)[:-3]

    @api.model
    def _get_default_name(self):
        today = fields.Date.today()
        return _('Meting of %s') % today

    @api.model
    def _get_default_company(self):
        return self.env.user.company_id

    name = fields.Char('Name', required=True, size=64, index=True, default=_get_default_name)
    date_begin = fields.Datetime('Begin', required=True)
    date_end = fields.Datetime('End')
    duration = fields.Char('Duration', readonly=True, compute='_get_duration')
    user_ids = fields.Many2many('res.users', string='Presents', ondelete='restrict')
    other_presents = fields.Char('Other Presents')
    meeting_president = fields.Char('Meeting President')
    meeting_secretary = fields.Char('Meeting Secretary')
    text_agenda = fields.Text('Agenda')
    text_report = fields.Text('Report')
    pad_report = fields.Char('Report', pad_content_field='text_report')
    decision_ids = fields.One2many('meeting.decision', 'meeting_id', string='Decisions')
    meeting_type_id = fields.Many2one('meeting.type', 'Type')
    address = fields.Char('Address')
    company_id = fields.Many2one('res.company', 'Company', ondelete='restrict', default=_get_default_company)

    _sql_constraints = [
        ('meeting_dates', "CHECK(date_begin <= date_end)", 'Begin date cannot be after end date!'),
    ]

    @api.multi
    def get_presents(self):
        self.ensure_one()
        presents = ''
        if self.user_ids:
            presents += ', '.join(self.user_ids.mapped('name'))
        if self.other_presents:
            if self.user_ids:
                presents += ', '
            presents += self.other_presents
        return presents
