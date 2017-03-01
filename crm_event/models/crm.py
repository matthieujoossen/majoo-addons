# -*- coding: utf-8 -*-

from odoo import models, api, fields


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.multi
    def add_meeting(self):
        self.ensure_one()
        partner_ids = self.env.user.partner_id.ids
        if self.partner_id:
            partner_ids.append(self.partner_id.id)
        context = {'default_opportunity_id': self.id if self.type == 'opportunity' else False,
                   'default_partner_id': self.partner_id.id,
                   'default_partner_ids': partner_ids,
                   'default_team_id': self.team_id.id,
                   'default_name': self.name,
        }
        return {'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'calendar.event',
                'res_id': False,
                'context': context,
                'target': 'new', }
