# -*- coding: utf-8 -*-

from odoo import models, api, fields, _


class ProjectTeamWorker(models.Model):
    _name = 'project.team_worker'
    _description = _('Team Worker')
    _order = 'name'

    @api.multi
    def _compute_projects(self):
        for team in self:
            projects = self.env['project.project'].search([('project_team_ids', 'in', team.id)])
            team.project_count = len(projects)

    name = fields.Char(string=_('Name'), required=True)
    project_count = fields.Integer(string=_('# Project'), compute='_compute_projects')
    user_ids = fields.Many2many('res.users', string=_('Users'))
    active = fields.Boolean(string=_('Active'), default=True)

    _sql_constraints = [
        ('unique_name', "UNIQUE(name)", _('Name must be unique!')), ]

    @api.multi
    def get_projects(self):
        self.ensure_one()
        domain = [('project_team_ids', 'in', self.id)]
        return {
            'name': _('Projects'),
            'domain': domain,
            'res_model': 'project.project',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'limit': 80,
        }


class ProjectProject(models.Model):
    _inherit = 'project.project'

    project_team_ids = fields.Many2many('project.team_worker', string=_('Teams'))
